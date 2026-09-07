# [M] Croc requires senders to provide local IP addresses in cleartext

## Summary
Severity: Medium
Advisory: GHSA-7mp6-929p-pqhj
CVE: CVE-2023-43618
CWE: CWE-311
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-7mp6-929p-pqhj
Type: github-advisory

## Affected
- Go: `github.com/schollz/croc/v9` — affected >=0 <9.6.16

## Details
An issue was discovered in Croc before 9.6.16. The protocol requires a sender to provide its local IP addresses in cleartext via an `ips?` message.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-43618
- https://github.com/schollz/croc/issues/597
- https://github.com/schollz/croc/pull/700
- https://github.com/schollz/croc/commit/6f5f16aa1c16b1ec6f31fec35be15de466d9701b
- https://github.com/schollz/croc
- https://www.openwall.com/lists/oss-security/2023/09/08/2
- http://www.openwall.com/lists/oss-security/2023/09/21/5
