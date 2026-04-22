import streamlit as st
import google.generativeai as genai
import time

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="DokumenKilat AI", page_icon="📄", layout="centered")

# --- JUDUL & DESKRIPSI ---
st.title("📄 DokumenKilat AI")
st.markdown("""
Buat dokumen resmi (Surat, Proposal, Laporan) dalam hitungan detik hanya dengan perintah sederhana.
**Fitur:** Generate Otomatis + Edit Mudah + Download Siap Cetak.
""")

# --- SIDEBAR UNTUK API KEY ---
with st.sidebar:
    st.header("⚙️ Pengaturan")
    api_key = st.text_input("Masukkan Google Gemini API Key", type="password")
    st.info("Dapatkan API Key gratis di: https://aistudio.google.com/app/apikey")
    st.markdown("---")
    st.write("Dibuat oleh Pak Dodi & Qwen AI 🚀")

# --- DAFTAR TEMPLATE ---
templates = {
    "Surat Izin Sekolah/Kuliah": "Buatkan surat izin tidak masuk sekolah/kuliah yang formal dan sopan. Sertakan alasan sakit/kepentingan, durasi waktu, dan permohonan maaf.",
    "Proposal Usaha UMKM Sederhana": "Buatkan kerangka proposal usaha kecil (UMKM) yang meyakinkan untuk modal bank/investor. Sertakan: Pendahuluan, Analisis Pasar, Rencana Produk, Estimasi Modal, dan Penutup.",
    "Laporan Praktikum/Sekolah": "Buatkan struktur laporan praktikum lengkap dengan: Tujuan, Dasar Teori, Alat Bahan, Langkah Kerja, Hasil Pengamatan, dan Kesimpulan.",
    "Surat Lamaran Kerja": "Buatkan surat lamaran kerja profesional yang menonjolkan keahlian dan motivasi. Format standar HRD Indonesia.",
    "Notulen Rapat Organisasi": "Buatkan format notulen rapat yang rapi mencakup: Daftar Hadir, Agenda, Pembahasan Utama, Keputusan, dan Tindak Lanjut."
}

# --- INPUT USER ---
col1, col2 = st.columns([2, 1])
with col1:
    selected_template = st.selectbox("Pilih Jenis Dokumen:", list(templates.keys()))
with col2:
    topic_detail = st.text_input("Topik/Judul Spesifik:", placeholder="Cth: Keripik Pisang Coklat")

additional_info = st.text_area("Detail Tambahan (Opsional):", placeholder="Cth: Nama saya Budi, kelas 12, sakit demam berdarah 3 hari...")

# --- TOMBOL GENERATE ---
if st.button("✨ Buat Dokumen Sekarang", type="primary"):
    if not api_key:
        st.error("❌ Mohon masukkan API Key di menu sebelah kiri terlebih dahulu!")
    elif not topic_detail and not additional_info:
        st.warning("⚠️ Mohon isi Topik atau Detail Tambahan agar hasil lebih akurat.")
    else:
        # Konfigurasi AI
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Menyusun Prompt Rahasia
        prompt_instruction = templates[selected_template]
        full_prompt = f"""
        Bertindaklah sebagai asisten administrasi profesional Indonesia. 
        Tugas: {prompt_instruction}
        
        Konteks Spesifik User:
        - Topik/Judul: {topic_detail}
        - Detail Tambahan: {additional_info}
        
        Instruksi Format:
        1. Gunakan Bahasa Indonesia baku (EYD) yang formal dan sopan.
        2. Berikan struktur yang jelas dengan Judul, Pembuka, Isi, dan Penutup.
        3. Gunakan tanda [ ... ] untuk bagian yang harus diisi manual oleh user (seperti Tanggal, Tanda Tangan, Nama Terang).
        4. Jangan berikan penjelasan pembuka seperti 'Tentu, ini drafnya'. Langsung berikan isi dokumennya saja.
        """

        with st.spinner("🤖 AI sedang menulis dokumen Anda..."):
            try:
                response = model.generate_content(full_prompt)
                doc_content = response.text
                
                # Simpan hasil ke session state agar tidak hilang saat edit
                st.session_state['generated_doc'] = doc_content
                st.success("✅ Dokumen berhasil dibuat!")
                
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

# --- AREA EDITOR (Hanya muncul jika sudah ada hasil) ---
if 'generated_doc' in st.session_state:
    st.markdown("### ✍️ Edit Dokumen Anda")
    st.caption("Anda bisa mengedit teks langsung di kotak bawah ini. Ubah bagian yang kurang pas, lalu download.")
    
    # Text Area untuk Edit Manual
    edited_doc = st.text_area(
        "Edit Konten:", 
        value=st.session_state['generated_doc'], 
        height=400,
        key="editor_area"
    )
    
    # Fitur Magic Rewrite Sederhana
    col_edit1, col_edit2 = st.columns(2)
    with col_edit1:
        if st.button("🔄 Perbaiki Bahasa (Lebih Formal)"):
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            refine_prompt = f"Perbaiki teks berikut agar lebih formal dan baku sesuai EYD, tanpa mengubah makna: \n\n{edited_doc}"
            refined_response = model.generate_content(refine_prompt)
            st.session_state['generated_doc'] = refined_response.text
            st.rerun()
            
    with col_edit2:
        if st.button("🔄 Ringkas Menjadi Lebih Pendek"):
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            refine_prompt = f"Ringkas teks berikut menjadi lebih padat dan to-the-point tanpa menghilangkan poin penting: \n\n{edited_doc}"
            refined_response = model.generate_content(refine_prompt)
            st.session_state['generated_doc'] = refined_response.text
            st.rerun()

    st.divider()
    
    # Tombol Download
    st.markdown("### 💾 Download Dokumen")
    st.download_button(
        label="📥 Download sebagai .txt (Bisa disalin ke Word)",
        data=edited_doc,
        file_name=f"Dokumen_{topic_detail.replace(' ', '_')}.txt",
        mime="text/plain"
    )
    st.caption("Tips: Setelah download, buka file .txt tersebut, Copy All, lalu Paste ke Microsoft Word.")
