# [C] Rejetto HFS < 3.2.1 Session Forgery via Predictable Signing Key

## Summary
Severity: Critical
Advisory: CVE-2026-61500
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-61500
Type: osv

## Details
Rejetto HFS 3.0.0 through 3.2.0 derives its session-cookie signing key from the non-cryptographic Math.random() generator and discloses outputs of the same generator to unauthenticated clients during login. A remote attacker can collect a small number of login responses, reconstruct the generator's state, recover the signing key, and forge a valid administrator session cookie, leading to full administrative access and remote code execution via the server_code configuration feature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61500.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-61500
- https://www.vulncheck.com/advisories/rejetto-hfs-session-forgery-via-predictable-signing-key
- https://github.com/rejetto/hfs/releases/tag/v3.2.1
- https://github.com/rejetto/hfs
