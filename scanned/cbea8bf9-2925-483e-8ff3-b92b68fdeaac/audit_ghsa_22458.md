# [H] MantisBT Incorrect Authorization for bug_revision_view_page.php check

## Summary
Severity: High
Advisory: GHSA-7j8m-fm49-xgmg
CVE: CVE-2020-35849
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7j8m-fm49-xgmg
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.24.4

## Details
An issue was discovered in MantisBT before 2.24.4. An incorrect access check in bug_revision_view_page.php allows an unprivileged attacker to view the Summary field of private issues, as well as bugnotes revisions, gaining access to potentially confidential information via the bugnote_id parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35849
- https://github.com/mantisbt/mantisbt/commit/e9fd168c519a46c2cd0f3cb835e9ce5dba77fc4d
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=27370
