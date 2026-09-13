# [M] GitPython before 3.1.59 Path Traversal via separate-git-dir

## Summary
Severity: Medium
Advisory: CVE-2026-78677
Aliases: GHSA-8mcc-hrx5-hvxc, PYSEC-2026-3787
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-78677
Type: osv

## Details
GitPython before 3.1.59 omits --separate-git-dir from unsafe_git_clone_options, allowing attackers to create arbitrary git directories outside the intended clone destination. Attackers can pass a separate_git_dir parameter to Repo.clone_from() or Repo.clone() to redirect repository metadata to an attacker-controlled filesystem path, enabling arbitrary directory creation and potential hook execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78677.json
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-8mcc-hrx5-hvxc
- https://nvd.nist.gov/vuln/detail/CVE-2026-78677
- https://www.vulncheck.com/advisories/gitpython-before-path-traversal-via-separate-git-dir
