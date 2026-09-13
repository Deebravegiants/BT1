# [H] CVE-2024-34199

## Summary
Severity: High
Advisory: CVE-2024-34199
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-05-10
Source: https://osv.dev/vulnerability/CVE-2024-34199
Type: osv

## Details
TinyWeb 1.94 and below allows unauthenticated remote attackers to cause a denial of service (Buffer Overflow) when sending excessively large elements in the request line.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34199.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-34199
- https://github.com/maximmasiutin/TinyWeb/commit/2584082
- https://github.com/maximmasiutin/TinyWeb/commit/d49c3da
- https://github.com/DMCERTCE/PoC_Tiny_Overflow
