# [M] filebrowser through 2.63.23 Denial of Service via named pipes

## Summary
Severity: Medium
Advisory: CVE-2026-82235
Aliases: GHSA-8q5j-8wcr-8v2v
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82235
Type: osv

## Details
filebrowser through 2.63.23 fails to validate named pipes in directory archive and public download handlers, allowing attackers to trigger blocking open syscalls. Authenticated users or anonymous visitors with public share links can repeatedly request archives containing named pipes to pin server goroutines and exhaust connection resources.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82235.json
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-8q5j-8wcr-8v2v
- https://nvd.nist.gov/vuln/detail/CVE-2026-82235
- https://www.vulncheck.com/advisories/filebrowser-through-2.63.23-denial-of-service-via-named-pipes
- https://github.com/filebrowser/filebrowser/commit/586d198d
