import os
import io

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, HRFlowable
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    letter = colors = getSampleStyleSheet = ParagraphStyle = SimpleDocTemplate = Paragraph = Spacer = RLImage = Table = TableStyle = HRFlowable = pdfmetrics = TTFont = None
    REPORTLAB_AVAILABLE = False


# Register TrueType fonts if available on Windows to support clean typography
FONT_REGULAR = 'Helvetica'
FONT_BOLD = 'Helvetica-Bold'
FONT_ITALIC = 'Helvetica-Oblique'
FONT_BOLD_ITALIC = 'Helvetica-BoldOblique'

if REPORTLAB_AVAILABLE and os.path.exists("C:/Windows/Fonts/arial.ttf"):
    try:
        pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))
        if os.path.exists("C:/Windows/Fonts/arialbi.ttf"):
            pdfmetrics.registerFont(TTFont('Arial-BoldItalic', 'C:/Windows/Fonts/arialbi.ttf'))
            FONT_BOLD_ITALIC = 'Arial-BoldItalic'
        FONT_REGULAR = 'Arial'
        FONT_BOLD = 'Arial-Bold'
        FONT_ITALIC = 'Arial-Italic'
    except Exception as e:
        print(f"[PDF] Arial registration note: {e}")


def clean_pdf_text(text):
    """Sanitize typography to prevent replacement characters and font encoding errors."""
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        '\u2014': ' -- ',   # em-dash
        '\u2013': ' - ',    # en-dash
        '\u2022': '&bull;', # bullet
        '\u2018': "'",      # left single quote
        '\u2019': "'",      # right single quote
        '\u201c': '"',      # left double quote
        '\u201d': '"',      # right double quote
        '\u2026': '...',    # ellipsis
        '\xa0': ' ',        # non-breaking space
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text


class PDFStorybookGenerator:
    """
    Generates a beautifully styled, publication-ready PDF Storybook
    including cover branding, embedded scene image, character dossier,
    act chapters, dialogue script callouts, and visual relevance score badge.
    """

    def generate_pdf(self, story_data, image_path, relevance_data=None, output_path=None):
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("ReportLab is not installed. Please run `pip install reportlab`.")

        buffer = None
        if output_path is None:
            buffer = io.BytesIO()
            doc_target = buffer
        else:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            doc_target = output_path

        doc = SimpleDocTemplate(
            doc_target,
            pagesize=letter,
            rightMargin=45,
            leftMargin=45,
            topMargin=45,
            bottomMargin=45
        )

        styles = getSampleStyleSheet()
        
        # Custom Theme Styles
        title_style = ParagraphStyle(
            'StoryTitle',
            parent=styles['Heading1'],
            fontName=FONT_BOLD,
            fontSize=24,
            leading=30,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=1, # Centered
            spaceAfter=8
        )

        subtitle_style = ParagraphStyle(
            'StorySubtitle',
            parent=styles['Normal'],
            fontName=FONT_ITALIC,
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor('#4a4e69'),
            alignment=1,
            spaceAfter=14
        )

        chapter_head_style = ParagraphStyle(
            'ChapterHead',
            parent=styles['Heading2'],
            fontName=FONT_BOLD,
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#22223b'),
            spaceBefore=10,
            spaceAfter=5
        )

        body_style = ParagraphStyle(
            'ChapterBody',
            parent=styles['Normal'],
            fontName=FONT_REGULAR,
            fontSize=10,
            leading=15,
            textColor=colors.HexColor('#2b2d42'),
            spaceAfter=8
        )

        dialogue_speaker_style = ParagraphStyle(
            'DialogueSpeaker',
            parent=styles['Normal'],
            fontName=FONT_BOLD,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#4361ee')
        )

        dialogue_text_style = ParagraphStyle(
            'DialogueText',
            parent=styles['Normal'],
            fontName=FONT_ITALIC,
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#1f2937')
        )

        story_elements = []

        # 1. Header Banner
        header_text = clean_pdf_text("<b>VISIONSTORY AI</b> &nbsp;|&nbsp; <i>Context-Aware Illustrated Storybook</i>")
        header_para = Paragraph(header_text, ParagraphStyle('HeaderBanner', fontName=FONT_REGULAR, fontSize=8.5, textColor=colors.HexColor('#6c757d'), alignment=1))
        story_elements.append(header_para)
        story_elements.append(Spacer(1, 10))

        # 2. Main Title & Meta
        title = clean_pdf_text(story_data.get("title", "The Journey Beyond"))
        story_elements.append(Paragraph(title, title_style))
        
        genre = clean_pdf_text(story_data.get("genre", "Adventure"))
        tone = clean_pdf_text(story_data.get("tone", "Emotional"))
        ending = clean_pdf_text(story_data.get("ending", "Happy"))
        scene = clean_pdf_text(story_data.get("scene_setting", "Picturesque Landscape"))
        
        meta_line = f"Genre: <b>{genre}</b> &nbsp;|&nbsp; Tone: <b>{tone}</b> &nbsp;|&nbsp; Ending: <b>{ending}</b> &nbsp;|&nbsp; Setting: <b>{scene}</b>"
        story_elements.append(Paragraph(meta_line, subtitle_style))
        story_elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=12))

        # 3. Image Embed (if available)
        if image_path and os.path.exists(image_path):
            try:
                img = RLImage(image_path, width=420, height=220)
                story_elements.append(img)
                story_elements.append(Spacer(1, 6))
                
                caption = clean_pdf_text(story_data.get("image_caption", "Original Visual Context"))
                caption_para = Paragraph(f"<i>Visual Grounding:</i> {caption}", ParagraphStyle('ImgCap', fontName=FONT_ITALIC, fontSize=9, leading=12, textColor=colors.HexColor('#64748b'), alignment=1))
                story_elements.append(caption_para)
                story_elements.append(Spacer(1, 14))
            except Exception as e:
                print(f"[PDF] Image embed warning: {e}")

        # 4. Character Profiles Table
        characters = story_data.get("characters", [])
        if characters:
            story_elements.append(Paragraph("Dramatis Personae (Extracted Characters)", chapter_head_style))
            char_rows = []
            for ch in characters:
                c_name = clean_pdf_text(ch.get('name', ''))
                c_role = clean_pdf_text(ch.get('role', ''))
                c_pers = clean_pdf_text(ch.get('personality', ''))
                c_vis = clean_pdf_text(ch.get('visual_connection', ''))
                char_info = Paragraph(
                    f"<b>{c_name}</b> &nbsp;-&nbsp; <i>{c_role}</i><br/>"
                    f"<font color='#4b5563'>Traits: {c_pers}</font><br/>"
                    f"<font color='#6b7280' size=8>Visual Tie-in: {c_vis}</font>",
                    body_style
                )
                char_rows.append([char_info])

            char_table = Table(char_rows, colWidths=[520])
            char_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            story_elements.append(char_table)
            story_elements.append(Spacer(1, 12))

        # 5. Chapters
        chapters = story_data.get("chapters", [])
        for ch in chapters:
            head = clean_pdf_text(ch.get("heading", f"Chapter {ch.get('number')}"))
            content = clean_pdf_text(ch.get("content", ""))
            story_elements.append(Paragraph(head, chapter_head_style))
            story_elements.append(Paragraph(content, body_style))

        # 6. Dialogue Script Callout Box
        dialogues = story_data.get("dialogue", [])
        if dialogues:
            story_elements.append(Spacer(1, 8))
            story_elements.append(Paragraph("Key Dialogues", chapter_head_style))
            diag_rows = []
            for d in dialogues:
                spk = Paragraph(f"<b>{clean_pdf_text(d.get('speaker', 'Speaker'))}:</b>", dialogue_speaker_style)
                txt = Paragraph(f"\"{clean_pdf_text(d.get('line', ''))}\"", dialogue_text_style)
                diag_rows.append([spk, txt])

            diag_table = Table(diag_rows, colWidths=[100, 420])
            diag_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4ff')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#c7d2fe')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ]))
            story_elements.append(diag_table)
            story_elements.append(Spacer(1, 10))

        # 7. Moral / Takeaway
        moral = story_data.get("moral")
        if moral:
            story_elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceBefore=8, spaceAfter=8))
            moral_p = Paragraph(f"<b>Moral of the Tale:</b> <i>\"{clean_pdf_text(moral)}\"</i>", ParagraphStyle('Moral', parent=body_style, fontSize=10.5, fontName=FONT_ITALIC, textColor=colors.HexColor('#1e293b'), alignment=1))
            story_elements.append(moral_p)

        # 8. Relevance Score Badge at Footer
        if relevance_data:
            score = relevance_data.get("overall_relevance_score", 92.0)
            breakdown = relevance_data.get("breakdown", {})
            ent_f = breakdown.get("entity_fidelity", 100)
            sc_a = breakdown.get("scene_alignment", 90)
            summary_note = clean_pdf_text(relevance_data.get('summary_note', ''))
            
            score_text = (
                f"<b>Vision-to-Story Relevance Score: {score}%</b> &nbsp;|&nbsp; "
                f"Entity Fidelity: {ent_f}% &nbsp;|&nbsp; Scene Alignment: {sc_a}%<br/>"
                f"<font size=7 color='#475569'>{summary_note}</font>"
            )
            score_table = Table([[Paragraph(score_text, ParagraphStyle('ScoreP', fontName=FONT_REGULAR, fontSize=8.5, leading=11, textColor=colors.HexColor('#0f172a'), alignment=1))]], colWidths=[520])
            score_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecfdf5')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#6ee7b7')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story_elements.append(Spacer(1, 12))
            story_elements.append(score_table)

        doc.build(story_elements)

        if output_path is None and buffer is not None:
            buffer.seek(0)
            return buffer.getvalue()
        return output_path or b""
