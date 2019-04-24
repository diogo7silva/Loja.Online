class Fatura:

    def envia_pdf(self, file, email):
        import smtplib, ssl
        import base64
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        subject = "An email with attachment from Python"
        body = "This is an email with attachment sent from Python"
        sender_email = "lojaonline.aemaximinos@gmail.com"
        receiver_email = email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message["Bcc"] = receiver_email  # Recommended for mass emails
        message.attach(MIMEText(body, "plain"))
        filename = 'static/faturas/' + file
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file}",
        )
        message.attach(part)
        text = message.as_string()
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, base64.b64decode(b'ZXNjb2xhc2VndXJh').decode())
            server.sendmail(sender_email, receiver_email, text)

    def merge_pdf(self, nome):
        from PyPDF2 import PdfFileReader, PdfFileWriter
        import os
        pasta = 'static/faturas/'
        if not os.path.exists(pasta):
            os.makedirs(pasta)
        tmp = PdfFileReader('static/template.pdf').getPage(0)
        tmp.mergePage(PdfFileReader('db/dados.pdf').getPage(0))
        fatura = PdfFileWriter()
        fatura.addPage(tmp)
        file = pasta + nome
        with open(file, 'wb') as fh:
            fatura.write(fh)

    def cria_pdf(self, loja):
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
        from reportlab.lib.pagesizes import A4
        from datetime import datetime, timedelta
        import time
        width, height = A4
        c = canvas.Canvas("db/dados.pdf", pagesize=A4)
        data = datetime.now().date()
        c.setFont('Helvetica-Bold', 10)
        c.drawRightString(width - 1.5 * cm, height - 8.2 * cm, str(data))
        c.drawRightString(width - 4 * cm, height - 8.2 * cm, str(data + timedelta(days=5)))
        c.drawRightString(width - 6.5 * cm, height - 8.2 * cm, str(loja.usr.cliente))
        linha = height - 9.3 * cm
        ls = 0.525 * cm
        c.setFont('Helvetica', 8)
        for li in range(loja.carrinho.__len__()):
            aux = loja.carrinho[li]
            c.drawCentredString(1.5 * cm, linha - (li * ls), str(aux.codigo))
            c.drawString(2.4 * cm, linha - (li * ls), str(aux.artigo))
            c.drawRightString(width - 4.85 * cm, linha - (li * ls), str(aux.quantidade))
            c.drawRightString(width - 3.32 * cm, linha - (li * ls), loja.moeda(aux.custo))
            c.drawRightString(width - 2.82 * cm, linha - (li * ls), str('23'))
            c.drawRightString(width - 1.07 * cm, linha - (li * ls), loja.moeda(aux.total()))
        c.drawString(7 * cm, 3.15 * cm, "(c) Copyright 2019 Paulo Côto - TESTE DE IMPRESSÃO")
        texto = c.beginText(10.8 * cm, height - 2.5 * cm)
        texto.setFont('Helvetica-Bold', 14)
        texto.textLine("Encomenda")
        texto.textLine(' ')
        texto.setFont('Helvetica', 10)
        texto.textLine("Exmo.(s) Sr.(s)")
        texto.textLine(' ')
        texto.setFont('Helvetica-Bold', 10)
        texto.textLine(loja.usr.nome)
        texto.setFont('Helvetica', 10)
        for line in loja.usr.morada.splitlines(False):
            texto.textLine(line.rstrip())
        texto.setFont('Helvetica-Bold', 10)
        texto.textLine(' ')
        texto.textLine('NIF: ' + loja.usr.nif)
        c.drawText(texto)
        total = loja.total()
        mercadorias = total / 1.23
        iva = total - mercadorias
        c.setFont('Helvetica', 10)
        s = 0.53
        b = 5.5
        c.drawRightString(width - 1.0 * cm, (4 * s + b) * cm, loja.moeda(mercadorias))
        c.drawRightString(width - 1.0 * cm, (3 * s + b) * cm, loja.moeda(0))
        c.drawRightString(width - 1.0 * cm, (2 * s + b) * cm, loja.moeda(0))
        c.drawRightString(width - 1.0 * cm, (1 * s + b) * cm, loja.moeda(iva))
        c.drawRightString(width - 1.0 * cm, (0 * s + b) * cm, loja.moeda(0))
        total_items = 0
        for linha in range(loja.carrinho.__len__()):
            total_items += loja.carrinho[linha].quantidade
        c.drawString(3.7 * cm, 8.67 * cm, str(total_items))
        c.setFont('Helvetica', 8)
        c.drawString(2.7 * cm, 6.65 * cm, loja.moeda(mercadorias))
        c.drawString(5.45 * cm, 6.65 * cm, loja.moeda(iva))
        c.setFont('Helvetica-Bold', 18)
        c.drawRightString(width - 1.0 * cm, 4.5 * cm, loja.moeda(total))
        # ----------------- QR CODE ----------------
        t = str(int(time.time() * 100000))
        code = t[10:12] + ' ' + t[12:15] + '/' + t[0:10]
        file = 'F' + t[10:15] + '_' + t[0:10] + '.pdf'
        c.setFont('Helvetica-Bold', 15)
        c.drawRightString(width - 1 * cm, height - 1.5 * cm, str(code))
        import qrcode
        qr = qrcode.QRCode()
        qr.add_data(code)
        img = qr.make_image(fill_color="#005", back_color="#ffe")
        c.drawInlineImage(img, width - 4 * cm, height - 4.6 * cm, width=3 * cm, height=3 * cm)
        # ------------------------------------------
        c.showPage()
        c.save()
        self.merge_pdf(file)
        # self.envia_pdf(file, loja.usr.email)
        return file
