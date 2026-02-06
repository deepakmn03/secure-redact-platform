import fitz  # PyMuPDF
import logging
import os
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFRedactionService:
    def __init__(self, input_path: str):
        """
        Initialize the service with the path to the PDF file.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"The file {input_path} does not exist.")
            
        self.input_path = input_path
        try:
            self.doc = fitz.open(self.input_path)
        except Exception as e:
            logger.error(f"Failed to open PDF: {e}")
            raise ValueError("Invalid or Corrupted PDF file")

    def _find_coordinates(self, page, term: str) -> List[fitz.Rect]:
        """
        Internal method to find coordinates of a specific text term on a page.
        """
        # search_for returns a list of Rect objects where the text was found.
        # quads=False ensures we get rectangular boxes, not quadrilaterals (simpler for redaction).
        return page.search_for(term, quads=False)

    def redact(self, target_words: List[str], output_path: str) -> str:
        """
        Main method to perform redaction.
        
        Args:
            target_words: List of strings to redact (e.g., ['secret', 'password'])
            output_path: Where to save the result
            
        Returns:
            str: The path to the redacted file
        """
        total_redactions = 0
        
        # 1. Iterate through every page in the PDF
        for page_num, page in enumerate(self.doc):
            
            # 2. Search for each target word
            for word in target_words:
                if not word.strip():
                    continue

                # Get coordinates of the word
                # We simply lowercase the word for search, but note that 
                # page.search_for is case-insensitive by default in newer PyMuPDF versions.
                rects = self._find_coordinates(page, word)
                
                if rects:
                    logger.info(f"Page {page_num + 1}: Found '{word}' {len(rects)} times.")

                # 3. Add Redaction Annotations
                for rect in rects:
                    # add_redact_annot marks the area for redaction.
                    # fill=(0, 0, 0) makes the box black.
                    page.add_redact_annot(
                        rect, 
                        text="", 
                        fill=(0, 0, 0)
                    )
                    total_redactions += 1

            # 4. Apply Redactions (Destructive Step)
            # images=fitz.PDF_REDACT_IMAGE_NONE ensures that if text overlaps an image,
            # the underlying image pixels are also removed.
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

        # 5. Security: Scrub Metadata
        # This removes Author, Title, Creator, etc.
        self.doc.set_metadata({}) 

        # 6. Save the file
        # garbage=4: Aggressive garbage collection to remove unused objects
        # deflate=True: Compresses the file streams
        try:
            self.doc.save(output_path, garbage=4, deflate=True)
            logger.info(f"Success! Saved redacted file to: {output_path}")
            logger.info(f"Total items redacted: {total_redactions}")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise
        finally:
            self.doc.close()
        
        return output_path

# --- TEST BLOCK ---
# This block only runs if you execute 'python redactor.py' directly.
if __name__ == "__main__":
    # Create a dummy PDF for testing if one doesn't exist
    test_input = "test_document.pdf"
    test_output = "test_document_redacted.pdf"
    
    if not os.path.exists(test_input):
        print(f"Generating dummy file '{test_input}' for testing...")
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 72), "This is a confidential document.\nThe password is supersecret.\nDo not share this confidential info.", fontsize=12)
        doc.save(test_input)
        doc.close()

    # Define words to redact
    words_to_redact = ["confidential", "password", "supersecret"]
    
    print(f"Redacting words: {words_to_redact}")
    
    # Run the redactor
    service = PDFRedactionService(test_input)
    service.redact(words_to_redact, test_output)
    
    print(f"Done! Check '{test_output}' to see the result.")