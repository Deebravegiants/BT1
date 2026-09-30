# [H] CVE-2026-51974

## Summary
Severity: High
Advisory: CVE-2026-51974
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-51974
Type: osv

## Details
An eval() injection vulnerability in the get_list function in modules/meta_parser.py in lllyasviel Fooocus 2.1.854 through 2.5.5 allows remote attackers to execute arbitrary Python code via a crafted styles payload in the EXIF metadata of an uploaded image file.

## References
- https://github.com/lllyasviel/Fooocus/blob/main/modules/meta_parser.py#L89
- https://mrbruh.com/fooocus/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/51xxx/CVE-2026-51974.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-51974
- https://github.com/lllyasviel/Fooocus/issues/4115
