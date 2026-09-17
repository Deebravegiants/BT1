# [M] OpenBullet2 0.3.2 NTLMv2 Hash Disclosure via UNC Path Proxy Source

## Summary
Severity: Medium
Advisory: CVE-2026-39908
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-39908
Type: osv

## Details
OpenBullet2 through version 0.3.2 on Windows contains a credential disclosure vulnerability that allows remote attackers to capture the NTLMv2 hash of the process user by configuring a job proxy source with a UNC path pointing to an attacker-controlled server. When the job starts, the application attempts to load proxies from the UNC path, triggering an SMB authentication attempt that discloses the NTLMv2 hash, which can then be relayed or cracked offline.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39908.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-39908
- https://www.vulncheck.com/advisories/openbullet2-ntlmv2-hash-disclosure-via-unc-path-proxy-source
- https://github.com/openbullet/openbullet2
- https://hackernoon.com/one-empty-header-to-admin-how-an-auth-bypass-breaks-openbullet2
