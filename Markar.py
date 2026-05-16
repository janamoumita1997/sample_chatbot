from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered


# Load models + convert
converter = PdfConverter(artifact_dict=create_model_dict())
rendered = converter("output.pdf")

# Extract text
text, _, images = text_from_rendered(rendered)

print(text)