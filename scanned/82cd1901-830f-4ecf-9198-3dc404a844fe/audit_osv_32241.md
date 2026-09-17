# [M] CVE-2025-26311

## Summary
Severity: Medium
Advisory: CVE-2025-26311
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-02-20
Source: https://osv.dev/vulnerability/CVE-2025-26311
Type: osv

## Details
Multiple memory leaks have been identified in the clip actions parsing functions (parseSWF_CLIPACTIONS and parseSWF_CLIPACTIONRECORD) in util/parser.c of libming v0.4.8, which allow attackers to cause a denial of service via a crafted SWF file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26311.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-26311
- https://github.com/libming/libming/issues/329
