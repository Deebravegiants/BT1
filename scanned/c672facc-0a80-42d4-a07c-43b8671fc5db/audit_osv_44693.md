# [M] SiYuan before v3.8.2 Unbounded Session Creation via Basic Auth

## Summary
Severity: Medium
Advisory: CVE-2026-85582
Aliases: GHSA-f4vj-ppp2-5hg4
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85582
Type: osv

## Details
SiYuan versions before v3.8.2 contain an unbounded session creation vulnerability in the publish-service Basic Auth handler that allows authenticated attackers to exhaust memory. Attackers can repeatedly authenticate with valid credentials to create persistent session entries without expiry or capacity limits, causing indefinite process memory growth and denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85582.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-f4vj-ppp2-5hg4
- https://nvd.nist.gov/vuln/detail/CVE-2026-85582
- https://www.vulncheck.com/advisories/siyuan-before-3.8.2-unbounded-session-creation-via-basic-auth
