# [C] GitPython before 3.1.59 Local File Content Disclosure via .gitmodules

## Summary
Severity: Critical
Advisory: CVE-2026-78675
Aliases: GHSA-7833-fr7j-v32q, PYSEC-2026-3785
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-78675
Type: osv

## Details
GitPython before 3.1.59 fails to disable merge_includes when parsing .gitmodules, allowing attackers to disclose local file content by including arbitrary file paths via [include] directives. Attackers can craft a malicious .gitmodules file with include directives pointing to sensitive files; when repo.submodules is accessed, GitConfigParser raises MissingSectionHeaderError embedding the target file's first line verbatim in the exception message.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78675.json
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-7833-fr7j-v32q
- https://nvd.nist.gov/vuln/detail/CVE-2026-78675
- https://www.vulncheck.com/advisories/gitpython-before-local-file-content-disclosure-via-gitmodules
