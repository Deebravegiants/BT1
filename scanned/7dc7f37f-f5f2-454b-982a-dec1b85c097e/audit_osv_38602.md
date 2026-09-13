# [C] Goshs - ArtiPACKED Vulnerability – GitHub Actions Credential Persistence

## Summary
Severity: Critical
Advisory: CVE-2026-40903
Aliases: GHSA-hpxj-9fgp-fhhf
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40903
Type: osv

## Details
goshs is a SimpleHTTPServer written in Go. Prior to 2.0.0-beta.6, goshs has an ArtiPACKED vulnerability. ArtiPACKED can lead to leakage of the GITHUB_TOKEN through workflow artifacts, even though the token is not present in the repository source code. This vulnerability is fixed in 2.0.0-beta.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40903.json
- https://github.com/patrickhener/goshs/security/advisories/GHSA-hpxj-9fgp-fhhf
- https://nvd.nist.gov/vuln/detail/CVE-2026-40903
