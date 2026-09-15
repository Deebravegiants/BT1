# [M] CVE-2020-8894

## Summary
Severity: Medium
Advisory: CVE-2020-8894
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-8894
Type: osv

## Details
An issue was discovered in MISP before 2.4.121. ACLs for discussion threads were mishandled in app/Controller/ThreadsController.php and app/Model/Thread.php.

## References
- https://zigrin.com/advisories/misp-mishandling-of-discussion-threads-acls/
- https://github.com/MISP/MISP/commit/9400b8bc8699435d84508e598aca98a31affd77c
- https://github.com/MISP/MISP/compare/v2.4.120...v2.4.121
