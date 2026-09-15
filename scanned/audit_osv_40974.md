# [M] CVE-2026-56406

## Summary
Severity: Medium
Advisory: CVE-2026-56406
CVSS: 6.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2026-56406
Type: osv

## Details
libexpat before 2.8.2 has an integer overflow in XML_ParseBuffer because it lacked a check that was present in XML_Parse.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56406.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56406
- https://github.com/libexpat/libexpat/pull/1255
