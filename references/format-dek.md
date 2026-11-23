# Format input

| Medan | Isi |
| --- | --- |
| `title` | Tajuk dek |
| `lang` | Kod bahasa seperti `ms` atau `en` |
| `slides` | Tatasusunan slaid mengikut urutan pembentangan |
| `slides[].id` | ID unik seperti `skop` |
| `slides[].title` | Tajuk slaid |
| `slides[].lead` | Mesej ringkas, pilihan |
| `slides[].layout` | `focus`, `columns` atau `sequence` |
| `slides[].items` | Senarai objek dengan `label` dan `text`, lalai kosong |
| `slides[].notes` | Nota pembentang, pilihan |
| `slides[].seconds` | Peruntukan masa slaid dalam saat, pilihan |
| `slides[].sources` | Senarai objek pilihan dengan `label` dan `url` HTTPS |

Guna `focus` untuk satu mesej dan beberapa butiran, `columns` untuk perbandingan dan `sequence` untuk langkah berurutan. Pecahkan kandungan yang padat kepada beberapa slaid. Letakkan huraian lisan dalam nota. Sumber yang menggunakan URL yang sama boleh diletakkan pada beberapa slaid jika relevan.

Dari akar folder skill, jalankan dengan Python 3. Gantikan `python` dengan `py` jika pemasangan Windows menggunakan pelancar itu.

```bash
python scripts/deck.py build examples/osi-model.json deck.html --style technical
python scripts/deck.py check deck.html --expect-seconds 180
```

Guna `--style editorial` untuk templat kedua. Selepas mengubah JSON, bina semula HTML. Skrip hanya menggunakan pustaka standard Python. Untuk bentuk visual tersuai, ubah HTML dengan menjaga struktur slaid, label aksesibiliti dan fungsi pembentang. Ulang semakan selepas edit manual.

Buka HTML dalam pelayar. Gunakan anak panah kiri dan kanan atau butang pada bar navigasi. Tekan butang **Pembentang** untuk panel nota, tajuk slaid seterusnya dan timer dalam tetingkap yang sama. Panel tidak membuka skrin penonton kedua. Gunakan paparan biasa ketika berkongsi skrin dengan audiens.
