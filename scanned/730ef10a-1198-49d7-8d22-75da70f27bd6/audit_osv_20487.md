# [C] CVE-2021-34187

## Summary
Severity: Critical
Advisory: CVE-2021-34187
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-28
Source: https://osv.dev/vulnerability/CVE-2021-34187
Type: osv

## Details
main/inc/ajax/model.ajax.php in Chamilo through 1.11.14 allows SQL Injection via the searchField, filters, or filters2 parameter.

## References
- https://github.com/chamilo/chamilo-lms/commit/005dc8e9eccc6ea35264064ae09e2e84af8d5b59
- https://github.com/chamilo/chamilo-lms/commit/f7f93579ed64765c2667910b9c24d031b0a00571
- https://support.chamilo.org/projects/1/wiki/Security_issues#Issue-67-2021-05-27-High-impact-very-high-risk-Unauthenticated-SQL-injection
- https://murat.one/?p=118
