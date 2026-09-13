# [C] Soko SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-28424
Aliases: GHSA-gc2x-86p3-mxg2
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-03-20
Source: https://osv.dev/vulnerability/CVE-2023-28424
Type: osv

## Details
Soko if the code that powers packages.gentoo.org. Prior to version 1.0.2, the two package search handlers, `Search` and `SearchFeed`, implemented in `pkg/app/handler/packages/search.go`, are affected by a SQL injection via the `q` parameter. As a result, unauthenticated attackers can execute arbitrary SQL queries on `https://packages.gentoo.org/`. It was also demonstrated that primitive was enough to gain code execution in the context of the PostgreSQL container. The issue was addressed in commit `4fa6e4b619c0362728955b6ec56eab0e0cbf1e23y` of version 1.0.2 using prepared statements to interpolate user-controlled data in SQL queries.

## References
- https://gitweb.gentoo.org/sites/soko.git/commit/?id=4fa6e4b619c0362728955b6ec56eab0e0cbf1e23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28424.json
- https://github.com/gentoo/soko/security/advisories/GHSA-gc2x-86p3-mxg2
- https://nvd.nist.gov/vuln/detail/CVE-2023-28424
- https://www.sonarsource.com/blog/why-orms-and-prepared-statements-cant-always-win
