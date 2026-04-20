# Deploy ke Railway

Project ini harus dideploy menggunakan Docker karena Playwright membutuhkan dependensi sistem native yang tidak tersedia di default Railway Python build.

1. Buat repository baru di GitHub.
2. Dari folder project ini:
   ```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <GITHUB_REPO_URL>
git push -u origin main
```
3. Di Railway:
   - Login ke https://railway.app
   - Pilih "New Project" -> "Deploy from GitHub"
   - Hubungkan repo GitHub yang baru dibuat
   - Pilih project yang berisi `Dockerfile`
   - Railway akan mendeteksi Docker secara otomatis dan membuild image dari `Dockerfile`

> Jangan gunakan Railway Python build default untuk Playwright. Build default biasanya tidak menyertakan `libglib-2.0.so.0` dan library Chromium lain.

4. Jika menggunakan Railway CLI, jalankan sebagai Docker project:
   ```bash
npm install -g railway
railway login
railway init
railway up --docker
```

5. `Dockerfile` sudah menggunakan image resmi Playwright Python yang menyertakan Chromium dan semua dependensi native.

Catatan:
- Railway free tier masih bisa digunakan untuk development, tapi perhatikan batas pemakaian.
- `Procfile` dan `start.sh` tetap berguna untuk local testing, tetapi Railway production harus deploy lewat Docker agar Playwright bisa berjalan.
