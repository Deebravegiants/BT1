# [M] eml_parser: Path Traversal in Official Example Script Leads to Arbitrary File Write

## Summary
Severity: Medium
Advisory: GHSA-389r-rccm-h3h5
CVE: CVE-2026-29780
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-389r-rccm-h3h5
Type: github-advisory

## Affected
- PyPI: `eml-parser` — affected >=0 <2.0.1

## Details
### Summary
The official example script `examples/recursively_extract_attachments.py` contains a path traversal vulnerability that allows arbitrary file write outside the intended output directory. Attachment filenames extracted from parsed emails are directly used to construct output file paths without any sanitization, allowing an attacker-controlled filename to escape the target directory.

### Details
File: `examples/recursively_extract_attachments.py`
Lines: 61–64
```python
for a in m['attachment']:
    out_filepath = out_path / a['filename']  # No sanitization
    print(f'\tWriting attachment: {out_filepath}')
    with out_filepath.open('wb') as a_out:
        a_out.write(base64.b64decode(a['raw']))
```

The value `a['filename']` is attacker-controlled via crafted email attachment headers:
```
Content-Disposition: attachment; filename="../outside/pwned.txt"
```

No path normalization or boundary validation is performed before writing.

### PoC
1. Create a malicious `.eml` file:
```
Content-Disposition: attachment; filename="../outside/pwned.txt"
```
2. Run the example script:
```
python recursively_extract_attachments.py -p ./emails -o ./safe
```
3. Expected: `./safe/pwned.txt`  
4. Actual: `./outside/pwned.txt` ← written outside the intended directory

Verified on Kali Linux with eml_parser installed via pip in a virtual environment.

### Impact
This vulnerability is limited to the **example script only** and does not affect the core eml_parser library. However, as the script is part of the official repository and is likely to be adapted for production use, an attacker supplying a crafted email could achieve arbitrary file write within the execution context.

Potential attack scenarios include:
- Cron job injection: `filename="../../etc/cron.d/backdoor"`
- Web shell upload: `filename="../../var/www/html/shell.php"`
- SSH key injection: `filename="../../home/user/.ssh/authorized_keys"`

### Recommended Fix
```python
import os.path

for a in m['attachment']:
    filename = os.path.basename(a['filename'])
    out_filepath = out_path / filename

    if not out_filepath.resolve().is_relative_to(out_path.resolve()):
        print(f'[!] Skipping suspicious filename: {a["filename"]}')
        continue

    print(f'\tWriting attachment: {out_filepath}')
    with out_filepath.open('wb') as a_out:
        a_out.write(base64.b64decode(a['raw']))
```

## References
- https://github.com/GOVCERT-LU/eml_parser/security/advisories/GHSA-389r-rccm-h3h5
- https://nvd.nist.gov/vuln/detail/CVE-2026-29780
- https://github.com/GOVCERT-LU/eml_parser/issues/88
- https://github.com/GOVCERT-LU/eml_parser/commit/99af03a09a90aaaaadd0ed2ffb5eea46d1ea2cc9
- https://github.com/GOVCERT-LU/eml_parser
