# [M] pip has an interpretation conflict due to handling both concatenated tar and ZIP files as ZIP files

## Summary
Severity: Medium
Advisory: GHSA-58qw-9mgm-455v
CVE: CVE-2026-3219
CWE: CWE-434
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-20
Source: https://github.com/advisories/GHSA-58qw-9mgm-455v
Type: github-advisory

## Affected
- PyPI: `pip` — affected >=0 <26.1

## Details
pip handles concatenated tar and ZIP files as ZIP files regardless of filename or whether a file is both a tar and ZIP file. This behavior could result in confusing installation behavior, such as installing "incorrect" files according to the filename of the archive. New behavior only proceeds with installation if the file identifies uniquely as a ZIP or tar archive, not as both.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-3219
- https://github.com/pypa/pip/issues/13867
- https://github.com/pypa/pip/pull/13870
- https://github.com/pypa/pip
- https://mail.python.org/archives/list/security-announce@python.org/thread/QAJ5JIVWWCAJ4EZL2FP5MOOW35JS7LRJ
- http://www.openwall.com/lists/oss-security/2026/04/20/8
