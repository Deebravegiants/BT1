# [H] CVE-2025-26305

## Summary
Severity: High
Advisory: CVE-2025-26305
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-02-20
Source: https://osv.dev/vulnerability/CVE-2025-26305
Type: osv

## Details
A memory leak has been identified in the parseSWF_SOUNDINFO function in util/parser.c of libming v0.4.8, which allows attackers to cause a denial of service via a crafted SWF file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26305.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-26305
- https://github.com/libming/libming/issues/322
