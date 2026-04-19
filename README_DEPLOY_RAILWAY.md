# Deploy ke Railway

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
   - Railway akan mendeteksi Python karena ada `requirements.txt`
   - Pastikan `Procfile` dan `start.sh` sudah ada di root project
4. Railway akan membuild paket, lalu menjalankan:
   ```bash
   bash ./start.sh
   ```

> `start.sh` akan menginstall Chromium untuk Playwright dan menjalankan `uvicorn`.

5. Jika ingin deploy tanpa GitHub, install CLI Railway:
   ```bash
npm install -g railway
railway login
railway init
railway up
```

Catatan:
- Railway free tier ada batas pemakaian, tapi sudah cukup untuk development.
- Pastikan file `requirements.txt` berisi `playwright`, `fastapi`, `uvicorn`, dll.
