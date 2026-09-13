# [H] CVE-2025-51663

## Summary
Severity: High
Advisory: CVE-2025-51663
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-51663
Type: osv

## Details
A vulnerability found in IPRateLimit implementation of FileCodeBox up to 2.2 allows remote attackers to bypass ip-based rate limit protection and failed attempt restrictions by faking X-Real-IP and X-Forwarded-For HTTP headers. This can enable attackers to perform DoS attacks or brute force share codes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51663.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51663
- https://github.com/vastsa/FileCodeBox/issues/350
- https://github.com/vastsa/FileCodeBox
