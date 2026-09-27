# [C] GitPython before 3.1.60 Remote Code Execution via Git Directory Impersonation

## Summary
Severity: Critical
Advisory: CVE-2026-87817
Aliases: GHSA-239g-whfq-7xj9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87817
Type: osv

## Details
GitPython before 3.1.60 fails to properly validate the git directory location, allowing attackers to impersonate the git directory using tracked files like gitdir, commondir, and HEAD. Attackers can execute arbitrary code by placing a malicious pre-commit hook in the tracked hooks directory that executes when a victim calls index.commit() on a cloned or opened repository.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87817.json
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-239g-whfq-7xj9
- https://nvd.nist.gov/vuln/detail/CVE-2026-87817
- https://www.vulncheck.com/advisories/gitpython-before-3.1.60-remote-code-execution-via-git-directory-impersonation
