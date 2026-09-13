# [M] CVE-2024-46657

## Summary
Severity: Medium
Advisory: CVE-2024-46657
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-12-10
Source: https://osv.dev/vulnerability/CVE-2024-46657
Type: osv

## Details
Artifex Software mupdf v1.24.9 was discovered to contain a segmentation fault via the component /tools/pdfextract.c. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted PDF file.

## References
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/diff/?id=b5c898a30f068b5342e8263a2cd5b9f0be291aac
- https://gist.github.com/isumitpatel/615e6bd2621cb46b5d980ddb9db223e2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46657.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46657
- https://github.com/ArtifexSoftware/mupdf/commit/b5c898a30f068b5342e8263a2cd5b9f0be291aac
