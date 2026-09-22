# [H] CVE-2020-8893

## Summary
Severity: High
Advisory: CVE-2020-8893
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-8893
Type: osv

## Details
An issue was discovered in MISP before 2.4.121. The Galaxy view contained an incorrectly sanitized search string in app/View/Galaxies/view.ctp.

## References
- https://zigrin.com/advisories/misp-bruteforce-protection-not-working-in-very-specific-environments/
- https://zigrin.com/advisories/misp-reflected-xss-in-galaxy-view/
- https://github.com/MISP/MISP/commit/3d982d92fd26584115c01f8c560a688d1096b65c
- https://github.com/MISP/MISP/compare/v2.4.120...v2.4.121
