import streamlit as st
import fitz  # PyMuPDF
import io
from PIL import Image

st.set_page_config(page_title="PDF Ultra Optimizer", page_icon="🚀")

st.title("🚀 PDF Ultra Optimizer")
st.write("Optimasi tingkat tinggi dengan kompresi gambar dan pembersihan objek.")

# Pengaturan di Sidebar
st.sidebar.header("Parameter Optimasi")
quality = st.sidebar.slider("Kualitas Gambar (1-100)", 10, 100, 75)
zoom = st.sidebar.slider("Skala Resolusi (0.5 - 1.0)", 0.5, 1.0, 0.85)

uploaded_file = st.file_uploader("Unggah PDF", type="pdf")

if uploaded_file:
    original_data = uploaded_file.read()
    st.info(f"Ukuran Asli: {len(original_data) / 1024:.2f} KB")

    if st.button("Kompres Maksimal"):
        with st.spinner("Sedang melakukan re-rendering setiap halaman..."):
            try:
                doc = fitz.open(stream=original_data, filetype="pdf")
                out_doc = fitz.open()  # Dokumen baru untuk output

                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    
                    # 1. Render halaman menjadi gambar (pixmap)
                    # Menggunakan matrix untuk downsampling (memperkecil resolusi)
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                    
                    # 2. Kompresi gambar menggunakan format JPEG
                    img_data = pix.tobytes("jpg", jpg_quality=quality)
                    
                    # 3. Masukkan kembali gambar ke halaman baru
                    new_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
                    new_page.insert_image(page.rect, stream=img_data)

                # Simpan dengan optimasi struktur
                output_buffer = io.BytesIO()
                out_doc.save(
                    output_buffer,
                    garbage=4,
                    deflate=True,
                    clean=True
                )
                
                final_data = output_buffer.getvalue()
                saving = (len(original_data) - len(final_data)) / len(original_data) * 100

                st.success(f"Optimasi Selesai! Ukuran berkurang {saving:.2f}%")
                st.metric("Ukuran Akhir", f"{len(final_data) / 1024:.2f} KB")

                st.download_button(
                    label="Download PDF Terkompresi",
                    data=final_data,
                    file_name=f"ultra_compressed_{uploaded_file.name}",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Terjadi kesalahan teknis: {e}")

st.sidebar.markdown("---")
st.sidebar.caption("© 2024 Optimus PDF v1.0")

st.sidebar.info("Developed by Karma")
