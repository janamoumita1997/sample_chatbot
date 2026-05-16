from pypdf import PdfReader,PdfWriter

reader = PdfReader("/home/moumita/Ncrt_class_10th_book/jesc1dd/jesc101.pdf")
writer = PdfWriter()

writer.add_page(reader.pages[0])

with open("output.pdf",'wb') as f:
    writer.write(f)