# [H] CVE-2021-42560

## Summary
Severity: High
Advisory: CVE-2021-42560
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-42560
Type: osv

## Details
An issue was discovered in CALDERA 2.9.0. The Debrief plugin receives base64 encoded "SVG" parameters when generating a PDF document. These SVG documents are parsed in an unsafe manner and can be leveraged for XXE attacks (e.g., File Exfiltration, Server Side Request Forgery, Out of Band Exfiltration, etc.).

## References
- https://github.com/mitre/caldera/releases
- https://github.com/DrunkenShells/Disclosures/tree/master/CVE-2021-42560-Unsafe%20XML%20Parsing-MITRE%20Caldera
