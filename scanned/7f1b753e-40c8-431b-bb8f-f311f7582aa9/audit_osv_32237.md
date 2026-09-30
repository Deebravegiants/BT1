# [M] CVE-2025-26307

## Summary
Severity: Medium
Advisory: CVE-2025-26307
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-02-20
Source: https://osv.dev/vulnerability/CVE-2025-26307
Type: osv

## Details
A memory leak has been identified in the parseSWF_IMPORTASSETS2 function in util/parser.c of libming v0.4.8, which allows attackers to cause a denial of service via a crafted SWF file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26307.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-26307
- https://github.com/libming/libming/issues/325
