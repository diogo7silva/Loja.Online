from flask import Flask, render_template, request, redirect
from models import lojaOnline

app = Flask(__name__)
loja = lojaOnline()


@app.route('/')
def index():
    return render_template('index.html', loja=loja)


@app.route('/encomenda')
def encomenda():
    fatura = loja.fatura
    loja.reset()
    return render_template('encomenda.html', loja=loja, fatura=fatura)


@app.route('/pr_ini/<produto>')
def products_ini(produto):
    loja.pagina = 0
    target = '/pr/' + produto
    return redirect(target)


@app.route('/pr/<produto>')
def products(produto):
    return render_template('produtos.html', loja=loja, folha=loja.livro[produto])


@app.route('/add/<produto>/<int:linha>')
def addcarrinho(produto, linha):
    loja.addcarrinho(produto, linha)
    return redirect(request.referrer)


@app.route('/mover/<int:valor>')
def mover(valor):
    loja.pagina += valor - 1
    return redirect(request.referrer)


@app.route('/pagina/<int:pagina>')
def pagina(pagina):
    loja.pagina = pagina - 1
    return redirect(request.referrer)


@app.route('/carrinho_ini')
def showcarrinho_ini():
    loja.pagina = 0
    return redirect('/carrinho')


@app.route('/carrinho', methods=['GET', 'POST'])
def showcarrinho():
    if request.method == 'POST':
        loja.usr.nif = request.form['nif']
        loja.usr.nome = request.form['nome']
        loja.usr.morada = request.form['morada']
        loja.usr.update()
        try:
            from fatura import Fatura
            loja.fatura = Fatura().cria_pdf(loja)
        except:
            loja.fatura = 'Brevemente.pdf'
        loja.encomenda()
        return redirect('/encomenda')
    return render_template('carrinho.html', loja=loja)


@app.route('/encomendar')
def encomendar():
    loja.encomendar = True
    return redirect(request.referrer)


@app.route('/sub/<int:linha>')
def subcarrinho(linha):
    loja.subcarrinho(linha)
    return redirect(request.referrer)


@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usr = request.form['utilizador']
        passes = loja.usr.passes()
        # Se o utilizador existe e a passe está correta:
        if usr in passes and passes[usr] == loja.usr.code(request.form['passe']):
            loja.usr.set(request.form['utilizador'])
            return redirect('/')
        elif usr not in passes:
            erro = 'O utilizador não existe.'
        else:
            erro = 'A palavra passe está incorreta.'
    return render_template('login.html', loja=loja, erro=erro)


@app.route('/registo', methods=['GET', 'POST'])
def registo():
    erro = None
    if request.method == 'POST':
        if request.form['utilizador'] in loja.usr.passes():
            erro = 'O utilizador já existe.'
        elif request.form['passe'] != request.form['cpasse']:
            erro = 'A palavra passe não coincide.'
        else:
            usr = request.form['utilizador']
            loja.usr.save(usr, request.form['email'], request.form['passe'])
            loja.usr.set(usr)
            return redirect('/')
    return render_template('registo.html', loja=loja, erro=erro)


@app.route('/logout')
def logout():
    loja.reset()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
