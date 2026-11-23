# Bina Dek Web

Skill untuk menukar nota, dokumen dan rangka kepada pembentangan HTML satu fail. Pilih gaya **Editorial** untuk naratif atau **Teknikal** untuk proses dan perbandingan. Paparan pembentang menyediakan nota, tajuk slaid seterusnya dan pemasa dalam tetingkap yang sama.

## Cuba contoh

Buka [dek Model OSI](examples/osi-model.html) dalam pelayar. Gunakan butang navigasi atau kekunci anak panah. Klik **Pembentang** untuk melihat nota dan pemasa.

## Bina dek

Perlukan Python 3. Jalankan dari akar projek.

```bash
python scripts/deck.py build examples/osi-model.json deck.html --style technical
python scripts/deck.py check deck.html --expect-seconds 180
```

Gantikan `technical` dengan `editorial` untuk gaya kedua. Pada Windows, gunakan `py` jika `python` tidak tersedia. Rujuk [format input](references/format-dek.md) untuk bina dek sendiri dan [SKILL.md](SKILL.md) untuk aliran kerja ejen.

## Kredit dan lesen

Aliran kerja pembentangan web diilhamkan oleh [Guizang PPT Skill](https://github.com/op7418/guizang-ppt-skill). Bina Dek Web menggunakan kod dan templat yang ditulis untuk projek ini.

Dilesenkan di bawah [MIT](LICENSE).
