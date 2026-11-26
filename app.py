import os
from datetime import datetime
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

st.set_page_config(page_title="WF SOM - Gerador de Documentos", page_icon="📄", layout="centered")


def parse_obs_lines(raw_text):
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def build_pdf_bytes(
    doc_type,
    service_label,
    client_name,
    details,
    included_items,
    service_items,
    obs_blocks,
    subtotal_sem_desconto,
    total_desconto,
    total_final,
    output_path
):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    border_color = colors.HexColor("#000000")
    text_color = colors.HexColor("#2D3748")
    header_bg = colors.HexColor("#E2E8F0")
    alt_bg = colors.HexColor("#F7FAFC")

    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1A202C"),
        fontName='Helvetica-Bold',
        alignment=1,
        spaceAfter=15
    )

    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=text_color,
        fontName='Helvetica'
    )

    header_table_style = ParagraphStyle(
        'HeaderTableStyle',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1A202C"),
        fontName='Helvetica-Bold'
    )

    story = []

    logo_path = 'logo_wf.png'
    if os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=200, height=83)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 10))
        except Exception as e:
            st.warning(f"Aviso ao carregar logo_wf.png: {e}")

    doc_title = (
        f"{doc_type.upper()} - {service_label.upper()}"
        if doc_type == "Recibo Rápido"
        else f"{doc_type.upper()} DE {service_label.upper()}"
    )
    story.append(Paragraph(doc_title, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=border_color, spaceAfter=15))

    data_hoje = datetime.now().strftime("%d/%m/%Y")
    info_data = [
        [Paragraph(f"<b>Cliente:</b> {client_name if client_name else 'Não informado'}", normal_style),
         Paragraph(f"<b>Data:</b> {data_hoje}", normal_style)]
    ]
    info_table = Table(info_data, colWidths=[380, 160])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))

    if details:
        story.append(Paragraph(
            "<b>ESPECIFICAÇÕES DO SISTEMA</b>",
            ParagraphStyle('SecHead', parent=normal_style, fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor("#1A202C"))
        ))
        story.append(Spacer(1, 6))
        det_data = [[Paragraph(f"<b>{k}:</b>", normal_style), Paragraph(str(v), normal_style)] for k, v in details.items()]
        det_table = Table(det_data, colWidths=[200, 340])
        det_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (0, -1), colors.white),
        ]))
        story.append(det_table)
        story.append(Spacer(1, 15))

    if included_items:
        story.append(Paragraph(
            "<b>ITENS INCLUSOS E MATERIAIS</b>",
            ParagraphStyle('SecHeadInc', parent=normal_style, fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor("#1A202C"))
        ))
        story.append(Spacer(1, 6))
        inc_data = [[Paragraph("<br/>".join([f"• {item}" for item in included_items]), normal_style)]]
        inc_table = Table(inc_data, colWidths=[540])
        inc_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))
        story.append(inc_table)
        story.append(Spacer(1, 15))

    if service_items:
        story.append(Paragraph(
            "<b>SERVIÇOS E VALORES</b>",
            ParagraphStyle('SecHead2', parent=normal_style, fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor("#1A202C"))
        ))
        story.append(Spacer(1, 6))
        table_data = [[
            Paragraph("Descrição do Serviço", header_table_style),
            Paragraph("Valor (R$)", header_table_style)
        ]]
        for srv in service_items:
            table_data.append([
                Paragraph(srv['desc'], normal_style),
                Paragraph(f"R$ {srv['val']:.2f}", normal_style)
            ])
        service_table = Table(table_data, colWidths=[380, 160])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_bg),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, alt_bg]),
        ]))
        story.append(service_table)
        story.append(Spacer(1, 15))

    if obs_blocks:
        story.append(Paragraph(
            "<b>OBSERVAÇÕES:</b>",
            ParagraphStyle('ObsHead', parent=normal_style, fontSize=10, fontName='Helvetica-Bold', textColor=colors.HexColor("#1A202C"))
        ))
        story.append(Spacer(1, 4))
        for titulo_obs, lista_obs in obs_blocks:
            for texto_obs in lista_obs:
                if texto_obs.strip():
                    story.append(Paragraph(f"<b>• {titulo_obs}:</b> {texto_obs.strip()}", normal_style))
        story.append(Spacer(1, 15))

    if total_desconto > 0:
        resumo_data = [
            [Paragraph("<b>VALOR TOTAL (SEM DESCONTO):</b>", normal_style),
             Paragraph(f"R$ {subtotal_sem_desconto:.2f}", ParagraphStyle('ValNormal', parent=normal_style, alignment=2))],
            [Paragraph("<b>DESCONTO APLICADO:</b>", normal_style),
             Paragraph(f"- R$ {total_desconto:.2f}", ParagraphStyle('ValDesc', parent=normal_style, alignment=2))],
            [Paragraph("<b>VALOR COM DESCONTO:</b>", ParagraphStyle('TotLbl', parent=normal_style, fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor("#1A202C"))),
             Paragraph(f"<b>R$ {total_final:.2f}</b>", ParagraphStyle('TotVal', parent=normal_style, fontSize=14, fontName='Helvetica-Bold', textColor=colors.HexColor("#1A202C"), alignment=2))]
        ]
        total_table = Table(resumo_data, colWidths=[260, 280])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 1), colors.white),
            ('BACKGROUND', (0, 2), (-1, 2), header_bg),
            ('GRID', (0, 0), (-1, -1), 0.5, border_color),
            ('BOX', (0, 0), (-1, -1), 1.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
    else:
        total_data = [
            [Paragraph("<b>VALOR TOTAL:</b>", ParagraphStyle('TotLbl', parent=normal_style, fontSize=12, fontName='Helvetica-Bold', textColor=colors.HexColor("#1A202C"))),
             Paragraph(f"<b>R$ {total_final:.2f}</b>", ParagraphStyle('TotVal', parent=normal_style, fontSize=14, fontName='Helvetica-Bold', textColor=colors.HexColor("#1A202C"), alignment=2))]
        ]
        total_table = Table(total_data, colWidths=[260, 280])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), header_bg),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1.5, border_color),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

    story.append(total_table)

    if "recibo" in doc_type.lower():
        story.append(Spacer(1, 40))
        story.append(HRFlowable(width="60%", thickness=1, color=border_color, spaceAfter=5, hAlign='CENTER'))
        story.append(Paragraph("Assinatura do Responsável", ParagraphStyle('Sig', parent=normal_style, alignment=1, fontSize=9, textColor=colors.HexColor("#718096"))))

    doc.build(story)
    with open(output_path, "rb") as f:
        return f.read()


st.title("WF SOM — Gerador de Documentos")

modo = st.radio(
    "O que você deseja gerar?",
    ["Orçamento", "Recibo", "Recibo Rápido"],
    horizontal=True
)

st.divider()

details = {}
included_items = []
service_items = []
obs_blocks = []
subtotal_sem_desconto = 0.0
total_desconto = 0.0

if modo == "Recibo Rápido":
    st.subheader("Recibo Rápido")
    client_name = st.text_input("Nome do Cliente")

    tipo_obs = st.radio(
        "A observação é de Instalação ou de Regulagem?",
        ["Instalação", "Regulagem", "Ambos (Instalação e Regulagem)"],
        horizontal=True
    )

    if tipo_obs in ["Instalação", "Ambos (Instalação e Regulagem)"]:
        obs_inst_raw = st.text_area("Observação(ões) de Instalação (uma por linha)")
        quer_mais_i = st.checkbox("Adicionar mais observações de Instalação?")
        if quer_mais_i:
            obs_inst_extra = st.text_area("Observações extras de Instalação (uma por linha)")
            obs_inst_list = parse_obs_lines(obs_inst_raw) + parse_obs_lines(obs_inst_extra)
        else:
            obs_inst_list = parse_obs_lines(obs_inst_raw)
        if obs_inst_list:
            obs_blocks.append(("Instalação", obs_inst_list))

    if tipo_obs in ["Regulagem", "Ambos (Instalação e Regulagem)"]:
        obs_reg_raw = st.text_area("Observação(ões) de Regulagem (uma por linha)")
        quer_mais_r = st.checkbox("Adicionar mais observações de Regulagem?")
        if quer_mais_r:
            obs_reg_extra = st.text_area("Observações extras de Regulagem (uma por linha)")
            obs_reg_list = parse_obs_lines(obs_reg_raw) + parse_obs_lines(obs_reg_extra)
        else:
            obs_reg_list = parse_obs_lines(obs_reg_raw)
        if obs_reg_list:
            obs_blocks.append(("Regulagem", obs_reg_list))

    st.markdown("#### Valores e Descontos")
    col_i1, col_i2 = st.columns(2)
    with col_i1:
        val_inst_normal = st.number_input("Valor da Instalação (R$)", min_value=0.0, step=10.0, format="%.2f")
        tem_desc_inst = st.checkbox("Aplicar desconto na Instalação?")
    with col_i2:
        val_desc_inst = st.number_input("Desconto da Instalação (R$)", min_value=0.0, step=5.0, format="%.2f", disabled=not tem_desc_inst)

    val_inst_final = max(0.0, val_inst_normal - val_desc_inst) if tem_desc_inst else val_inst_normal
    if val_inst_normal > 0 or tem_desc_inst:
        subtotal_sem_desconto += val_inst_normal
        total_desconto += min(val_inst_normal, val_desc_inst) if tem_desc_inst else 0.0
        desc_i = (
            f"Instalação (Valor: R$ {val_inst_normal:.2f} | Desconto: -R$ {val_desc_inst:.2f})"
            if tem_desc_inst and val_desc_inst > 0 else "Instalação"
        )
        service_items.append({"desc": desc_i, "val": val_inst_final})

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        val_reg_normal = st.number_input("Valor da Regulagem (R$)", min_value=0.0, step=10.0, format="%.2f")
        tem_desc_reg = st.checkbox("Aplicar desconto na Regulagem?")
    with col_r2:
        val_desc_reg = st.number_input("Desconto da Regulagem (R$)", min_value=0.0, step=5.0, format="%.2f", disabled=not tem_desc_reg)

    val_reg_final = max(0.0, val_reg_normal - val_desc_reg) if tem_desc_reg else val_reg_normal
    if val_reg_normal > 0 or tem_desc_reg:
        subtotal_sem_desconto += val_reg_normal
        total_desconto += min(val_reg_normal, val_desc_reg) if tem_desc_reg else 0.0
        desc_r = (
            f"Regulagem (Valor: R$ {val_reg_normal:.2f} | Desconto: -R$ {val_desc_reg:.2f})"
            if tem_desc_reg and val_desc_reg > 0 else "Regulagem"
        )
        service_items.append({"desc": desc_r, "val": val_reg_final})

    total_final = sum(s["val"] for s in service_items)
    if total_desconto > 0:
        st.info(f"**Valor Total:** R$ {subtotal_sem_desconto:.2f}  |  **Desconto:** -R$ {total_desconto:.2f}  |  **Valor com Desconto:** R$ {total_final:.2f}")
    else:
        st.info(f"**Valor Total:** R$ {total_final:.2f}")

    if st.button("Gerar PDF do Recibo Rápido", type="primary"):
        safe_name = client_name.strip().replace(" ", "_") if client_name.strip() else "Cliente"
        filename = f"Recibo_Rapido_{safe_name}.pdf"
        pdf_bytes = build_pdf_bytes(
            doc_type="Recibo Rápido",
            service_label=tipo_obs,
            client_name=client_name,
            details=details,
            included_items=included_items,
            service_items=service_items,
            obs_blocks=obs_blocks,
            subtotal_sem_desconto=subtotal_sem_desconto,
            total_desconto=total_desconto,
            total_final=total_final,
            output_path=filename
        )
        st.success(f"PDF gerado: {filename}")
        st.download_button("Baixar PDF", data=pdf_bytes, file_name=filename, mime="application/pdf")

else:
    servico = st.selectbox("Tipo de serviço", ["Instalação", "Regulagem", "Revisão"])
    client_name = st.text_input("Nome do Cliente (opcional)")

    if servico == "Revisão":
        tipo_rev = st.radio("Tipo de revisão", ["Revisão de Instalação", "Revisão de Regulagem"], horizontal=True)
        details["Tipo de Revisão"] = tipo_rev
        obs_rev_raw = st.text_area("Observação da revisão (uma por linha)")
        obs_rev_list = parse_obs_lines(obs_rev_raw)
        if obs_rev_list:
            obs_blocks.append(("Revisão", obs_rev_list))
        val_rev = st.number_input("Valor Total da Revisão (R$)", min_value=0.0, step=10.0, format="%.2f")
        subtotal_sem_desconto += val_rev
        service_items.append({"desc": f"Serviço de {tipo_rev}", "val": val_rev})

    elif servico == "Regulagem":
        sistema = st.radio("Alimentação do sistema", ["12V", "220V"], horizontal=True)
        details["Tipo de Sistema"] = sistema
        details["Quantidade de Amplificadores"] = st.text_input("Quantidade de amplificadores", value="0")
        details["Quantidade de Graves"] = st.text_input("Quantidade de graves", value="0")
        details["Quantidade de Médios"] = st.text_input("Quantidade de médios", value="0")
        details["Quantidade de Corneta"] = st.text_input("Quantidade de corneta", value="0")
        details["Quantidade de TI"] = st.text_input("Quantidade de TI", value="0")
        details["Quantidade de TWT"] = st.text_input("Quantidade de TWT", value="0")

        obs_reg_raw = st.text_area("Observação de Regulagem (uma por linha)")
        quer_mais_r = st.checkbox("Adicionar mais observações de Regulagem?")
        if quer_mais_r:
            obs_reg_extra = st.text_area("Observações extras de Regulagem (uma por linha)")
            obs_reg_list = parse_obs_lines(obs_reg_raw) + parse_obs_lines(obs_reg_extra)
        else:
            obs_reg_list = parse_obs_lines(obs_reg_raw)
        if obs_reg_list:
            obs_blocks.append(("Regulagem", obs_reg_list))

        val_reg_normal = st.number_input("Valor da Regulagem (R$)", min_value=0.0, step=10.0, format="%.2f")
        tem_desc_reg = st.checkbox("Vai ter desconto na regulagem?")
        val_desc_reg = st.number_input("Valor do Desconto na Regulagem (R$)", min_value=0.0, step=5.0, format="%.2f", disabled=not tem_desc_reg)
        val_reg_final = max(0.0, val_reg_normal - val_desc_reg) if tem_desc_reg else val_reg_normal

        subtotal_sem_desconto += val_reg_normal
        total_desconto += min(val_reg_normal, val_desc_reg) if tem_desc_reg else 0.0
        desc_r = (
            f"Serviço de Regulagem (Valor: R$ {val_reg_normal:.2f} | Desconto: -R$ {val_desc_reg:.2f})"
            if tem_desc_reg and val_desc_reg > 0 else "Serviço de Regulagem do Som"
        )
        service_items.append({"desc": desc_r, "val": val_reg_final})

    else:
        sistema = st.radio("Alimentação do sistema de som", ["12V", "220V"], horizontal=True)
        details["Tipo de Sistema"] = sistema
        if sistema == "12V":
            details["Quantidade de Baterias"] = st.text_input("Quantidade de baterias", value="0")
            details["Quantidade de Fontes"] = st.text_input("Quantidade de fontes", value="0")
        details["Quantidade de Amplificadores"] = st.text_input("Quantidade de amplificadores", value="0")
        details["Quantidade de Graves"] = st.text_input("Quantidade de graves", value="0")
        details["Quantidade de Médios"] = st.text_input("Quantidade de médios", value="0")
        details["Quantidade de Corneta"] = st.text_input("Quantidade de corneta", value="0")
        details["Quantidade de TI"] = st.text_input("Quantidade de TI", value="0")
        details["Quantidade de TWT"] = st.text_input("Quantidade de TWT", value="0")

        itens_raw = st.text_area("Itens inclusos e materiais (um por linha — já inclusos no preço da instalação)")
        included_items = parse_obs_lines(itens_raw)

        val_inst_normal = st.number_input("Valor da Instalação (R$)", min_value=0.0, step=10.0, format="%.2f")
        tem_desc_inst = st.checkbox("Vai ter desconto na instalação?")
        val_desc_inst = st.number_input("Valor do Desconto na Instalação (R$)", min_value=0.0, step=5.0, format="%.2f", disabled=not tem_desc_inst)
        val_inst_final = max(0.0, val_inst_normal - val_desc_inst) if tem_desc_inst else val_inst_normal

        subtotal_sem_desconto += val_inst_normal
        total_desconto += min(val_inst_normal, val_desc_inst) if tem_desc_inst else 0.0
        desc_i = (
            f"Serviço de Instalação (Valor: R$ {val_inst_normal:.2f} | Desconto: -R$ {val_desc_inst:.2f})"
            if tem_desc_inst and val_desc_inst > 0 else "Serviço de Instalação de Som"
        )
        service_items.append({"desc": desc_i, "val": val_inst_final})

        obs_inst_raw = st.text_area("Observações de Instalação (uma por linha)")
        quer_mais_i = st.checkbox("Adicionar mais observações de Instalação?")
        if quer_mais_i:
            obs_inst_extra = st.text_area("Observações extras de Instalação (uma por linha)")
            obs_inst_list = parse_obs_lines(obs_inst_raw) + parse_obs_lines(obs_inst_extra)
        else:
            obs_inst_list = parse_obs_lines(obs_inst_raw)
        if obs_inst_list:
            obs_blocks.append(("Instalação", obs_inst_list))

        incluir_reg = st.checkbox("Incluir regulagem?")
        if incluir_reg:
            val_reg_normal = st.number_input("Valor Normal da Regulagem (R$)", min_value=0.0, step=10.0, format="%.2f")
            tem_desc_reg = st.checkbox("Vai ter desconto na regulagem?")
            val_desc_reg = st.number_input("Valor do Desconto na Regulagem (R$)", min_value=0.0, step=5.0, format="%.2f", disabled=not tem_desc_reg)
            val_reg_final = max(0.0, val_reg_normal - val_desc_reg) if tem_desc_reg else val_reg_normal

            subtotal_sem_desconto += val_reg_normal
            total_desconto += min(val_reg_normal, val_desc_reg) if tem_desc_reg else 0.0
            desc_r = (
                f"Serviço de Regulagem (Valor: R$ {val_reg_normal:.2f} | Desconto: -R$ {val_desc_reg:.2f})"
                if tem_desc_reg and val_desc_reg > 0 else "Serviço de Regulagem do Som"
            )
            service_items.append({"desc": desc_r, "val": val_reg_final})

            obs_reg_raw = st.text_area("Observações de Regulagem (uma por linha)")
            quer_mais_r = st.checkbox("Adicionar mais observações de Regulagem?")
            if quer_mais_r:
                obs_reg_extra = st.text_area("Observações extras de Regulagem (uma por linha)")
                obs_reg_list = parse_obs_lines(obs_reg_raw) + parse_obs_lines(obs_reg_extra)
            else:
                obs_reg_list = parse_obs_lines(obs_reg_raw)
            if obs_reg_list:
                obs_blocks.append(("Regulagem", obs_reg_list))

    total_final = sum(s["val"] for s in service_items)
    if total_desconto > 0:
        st.info(f"**Valor Total:** R$ {subtotal_sem_desconto:.2f}  |  **Desconto:** -R$ {total_desconto:.2f}  |  **Valor com Desconto:** R$ {total_final:.2f}")
    else:
        st.info(f"**Valor Total:** R$ {total_final:.2f}")

    if st.button("Gerar PDF", type="primary"):
        safe_name = client_name.strip().replace(" ", "_") if client_name.strip() else "Cliente"
        filename = f"{modo}_{servico}_{safe_name}.pdf"
        pdf_bytes = build_pdf_bytes(
            doc_type=modo,
            service_label=servico,
            client_name=client_name,
            details=details,
            included_items=included_items,
            service_items=service_items,
            obs_blocks=obs_blocks,
            subtotal_sem_desconto=subtotal_sem_desconto,
            total_desconto=total_desconto,
            total_final=total_final,
            output_path=filename
        )
        st.success(f"PDF gerado: {filename}")
        st.download_button("Baixar PDF", data=pdf_bytes, file_name=filename, mime="application/pdf")
