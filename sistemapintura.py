# Sistema básico para oficina de lataria e pintura
# Stack: Python + Streamlit + SQLite (rodando na nuvem)

import streamlit as st
import sqlite3
from datetime import datetime

# Conexão com o banco de dados
conn = sqlite3.connect("oficina.db", check_same_thread=False)
c = conn.cursor()

# Criação das tabelas
c.execute('''CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    telefone TEXT,
    email TEXT,
    veiculo TEXT,
    placa TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS ordens_servico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    servico TEXT,
    valor REAL,
    status TEXT,
    data TEXT,
    FOREIGN KEY(cliente_id) REFERENCES clientes(id)
)''')

c.execute('''CREATE TABLE IF NOT EXISTS materiais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    quantidade INTEGER,
    unidade TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS financeiro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT,
    descricao TEXT,
    valor REAL,
    data TEXT
)''')

conn.commit()

# --- Interface Streamlit ---
st.title("🔧 Sistema da Oficina de Lataria e Pintura")

menu = st.sidebar.selectbox("Menu", ["Clientes", "Ordem de Serviço", "Materiais", "Financeiro", "Dashboard"])

if menu == "Clientes":
    st.header("Cadastro de Clientes")
    with st.form("form_cliente"):
        nome = st.text_input("Nome")
        telefone = st.text_input("Telefone")
        email = st.text_input("E-mail")
        veiculo = st.text_input("Veículo")
        placa = st.text_input("Placa")
        if st.form_submit_button("Salvar"):
            c.execute("INSERT INTO clientes (nome, telefone, email, veiculo, placa) VALUES (?, ?, ?, ?, ?)",
                      (nome, telefone, email, veiculo, placa))
            conn.commit()
            st.success("Cliente cadastrado com sucesso!")

elif menu == "Ordem de Serviço":
    st.header("Ordem de Serviço")
    clientes = c.execute("SELECT id, nome FROM clientes").fetchall()
    cliente_dict = {f"{nome} (ID {id})": id for id, nome in clientes}

    with st.form("form_os"):
        cliente_selecionado = st.selectbox("Cliente", list(cliente_dict.keys()))
        servico = st.text_area("Descrição do Serviço")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        status = st.selectbox("Status", ["Aguardando", "Em andamento", "Finalizada"])
        if st.form_submit_button("Salvar Ordem"):
            data = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO ordens_servico (cliente_id, servico, valor, status, data) VALUES (?, ?, ?, ?, ?)",
                      (cliente_dict[cliente_selecionado], servico, valor, status, data))
            conn.commit()
            st.success("Ordem de serviço cadastrada!")

elif menu == "Materiais":
    st.header("Controle de Materiais")
    with st.form("form_material"):
        nome = st.text_input("Nome do Material")
        quantidade = st.number_input("Quantidade", min_value=0)
        unidade = st.text_input("Unidade (ex: L, kg, un)")
        if st.form_submit_button("Adicionar"):
            c.execute("INSERT INTO materiais (nome, quantidade, unidade) VALUES (?, ?, ?)",
                      (nome, quantidade, unidade))
            conn.commit()
            st.success("Material adicionado!")

    st.subheader("Estoque Atual")
    materiais = c.execute("SELECT nome, quantidade, unidade FROM materiais").fetchall()
    st.table(materiais)

elif menu == "Financeiro":
    st.header("Controle Financeiro")
    with st.form("form_financeiro"):
        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
        if st.form_submit_button("Lançar"):
            data = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO financeiro (tipo, descricao, valor, data) VALUES (?, ?, ?, ?)",
                      (tipo, descricao, valor, data))
            conn.commit()
            st.success("Lançamento registrado!")

    st.subheader("Lançamentos Recentes")
    registros = c.execute("SELECT tipo, descricao, valor, data FROM financeiro ORDER BY data DESC LIMIT 10").fetchall()
    st.table(registros)

elif menu == "Dashboard":
    st.header("📊 Visão Geral")
    total_receitas = c.execute("SELECT SUM(valor) FROM financeiro WHERE tipo='Receita'").fetchone()[0] or 0
    total_despesas = c.execute("SELECT SUM(valor) FROM financeiro WHERE tipo='Despesa'").fetchone()[0] or 0
    lucro = total_receitas - total_despesas

    st.metric("Total de Receitas", f"R$ {total_receitas:.2f}")
    st.metric("Total de Despesas", f"R$ {total_despesas:.2f}")
    st.metric("Lucro", f"R$ {lucro:.2f}")
