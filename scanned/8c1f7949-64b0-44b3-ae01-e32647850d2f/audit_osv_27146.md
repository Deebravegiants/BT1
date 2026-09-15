# [H] Denial of Service in danny-avila/librechat

## Summary
Severity: High
Advisory: CVE-2024-11172
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-11172
Type: osv

## Details
A vulnerability in danny-avila/librechat version git a1647d7 allows an unauthenticated attacker to cause a denial of service by sending a crafted payload to the server. The middleware `checkBan` is not surrounded by a try-catch block, and an unhandled exception will cause the server to crash. This issue is fixed in version 0.7.6.

## References
- https://huntr.com/bounties/c76a7ee3-2e26-45a0-8940-21c749592105
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11172.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11172
- https://github.com/danny-avila/librechat/commit/976784c01fa4cce00d4c2941801d56aed375c21b
