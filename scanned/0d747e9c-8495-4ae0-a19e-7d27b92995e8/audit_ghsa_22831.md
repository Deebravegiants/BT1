# [M] MySQL for Node.js Unsafe Options

## Summary
Severity: Medium
Advisory: GHSA-f982-mxwc-3mrx
CVE: CVE-2019-14939
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-f982-mxwc-3mrx
Type: github-advisory

## Affected
- npm: `mysql` — affected >=2.17.1 <2.18.0

## Details
An issue was discovered in the mysql (aka mysqljs) module 2.17.1 for Node.js. `The LOAD DATA LOCAL INFILE` option is open by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14939
- https://github.com/mysqljs/mysql/issues/2471
- https://github.com/mysqljs/mysql/commit/337e87ae5fcea3667864197c65dc758517fcde06
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=934712&gt
- https://github.com/mysqljs/mysql
- https://web.archive.org/web/20190812004403/https://github.com/mysqljs/mysql/issues/2257
