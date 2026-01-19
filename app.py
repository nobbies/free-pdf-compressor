import streamlit as st
import fitz  # PyMuPDF
import io
import streamlit.components.v1 as components

# Konfigurasi Halaman Utama
st.set_page_config(
    page_title="PDF Zipper", 
    page_icon="📄", 
    layout="wide"
)

# --- SIDEBAR NAVIGASI ---
with st.sidebar:
    #st.title("📂 PDF Workspace")
    #st.info("Pilih layanan yang ingin Anda gunakan di bawah ini.")
    menu = st.radio(
        "Menu Utama:",
        ["Atur Halaman PDF", "Kompres PDF"],
        index=0
    )
    st.divider()
    st.caption("v1.2 - PDF Optimizer & Editor")

# --- KONTEN MENU 1: ATUR HALAMAN PDF ---
if menu == "Atur Halaman PDF":
    st.title("✂️ Atur Halaman PDF")
    st.write("Gunakan alat ini untuk menggabungkan beberapa PDF, menghapus halaman, atau mengubah rotasi.")
    
    # Membaca file atur_pdf.html
    try:
        with open("atur_pdf.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Menampilkan HTML/JS Editor (Diberi height cukup besar agar leluasa)
        components.html(html_content, height=900, scrolling=True)
        
    except FileNotFoundError:
        st.error("⚠️ File 'atur_pdf.html' tidak ditemukan di direktori yang sama dengan script ini.")
        st.info("Pastikan Anda sudah menyimpan konten HTML yang Anda berikan sebelumnya dengan nama 'atur_pdf.html'.")

# --- KONTEN MENU 2: KOMPRES PDF ---
elif menu == "Kompres PDF":
    st.title("🚀 PDF Ultra Optimizer")
    st.write("Perkecil ukuran file PDF Anda dengan teknik re-rendering dan kompresi JPEG.")

    uploaded_file = st.file_uploader("Pilih file PDF", type="pdf")

    # Layouting Parameter sebaris
    st.write("### Parameter Optimasi")
    col1, col2 = st.columns(2)
    
    with col1:
        quality = st.slider("Kualitas Gambar (1-100)", 10, 100, 75, help="Semakin rendah semakin kecil ukuran file, tapi gambar lebih buram.")
    
    with col2:
        zoom = st.slider("Skala Resolusi (0.1 - 1.0)", 0.1, 1.0, 0.85, help="0.5 berarti resolusi gambar dipotong menjadi setengahnya.")

    if uploaded_file:
        original_data = uploaded_file.read()
        file_size_kb = len(original_data) / 1024
        st.info(f"📦 Ukuran File Asli: {file_size_kb:.2f} KB")

        st.divider()

        if st.button("Mulai Proses Kompresi", use_container_width=True):
            with st.spinner("Sedang memproses... Mohon tunggu."):
                try:
                    # Membuka dokumen dari buffer
                    doc = fitz.open(stream=original_data, filetype="pdf")
                    out_doc = fitz.open()

                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        
                        # Render halaman menjadi gambar
                        mat = fitz.Matrix(zoom, zoom)
                        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                        
                        # Kompresi ke bytes JPG
                        img_data = pix.tobytes("jpg", jpg_quality=quality)
                        
                        # Masukkan ke halaman baru
                        new_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
                        new_page.insert_image(page.rect, stream=img_data)

                    # Simpan hasil akhir
                    output_buffer = io.BytesIO()
                    out_doc.save(
                        output_buffer,
                        garbage=4,
                        deflate=True,
                        clean=True
                    )
                    
                    final_data = output_buffer.getvalue()
                    final_size_kb = len(final_data) / 1024
                    saving = (len(original_data) - len(final_data)) / len(original_data) * 100

                    # Tampilkan Hasil
                    st.success(f"Berhasil! Ukuran berkurang sebesar {saving:.2f}%")
                    
                    m_col1, m_col2 = st.columns(2)
                    m_col1.metric("Ukuran Akhir", f"{final_size_kb:.2f} KB")
                    m_col2.metric("Hemat Ruang", f"{saving:.1f}%")

                    st.download_button(
                        label="📥 Download PDF Terkompresi",
                        data=final_data,
                        file_name=f"compressed_{uploaded_file.name}",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    doc.close()
                    out_doc.close()
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan teknis: {str(e)}")
