# [M] GitPython before 3.1.59 Arbitrary File Read via Repo.blame()

## Summary
Severity: Medium
Advisory: CVE-2026-78678
Aliases: GHSA-5xxx-qhh7-9287, PYSEC-2026-3788
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-78678
Type: osv

## Details
GitPython versions before 3.1.59 contain an incomplete denylist in the unsafe_git_revision_options guard that omits --contents and -S options, allowing attackers to read arbitrary files by passing these options to Repo.blame(). Attackers can supply revision values like --contents=/etc/passwd to leak file contents through the blame result returned to the caller.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78678.json
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-5xxx-qhh7-9287
- https://nvd.nist.gov/vuln/detail/CVE-2026-78678
- https://www.vulncheck.com/advisories/gitpython-before-arbitrary-file-read-via-repo-blame
