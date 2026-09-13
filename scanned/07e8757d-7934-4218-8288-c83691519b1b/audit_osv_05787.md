# [H] BIT-gulp-2021-35065

## Summary
Severity: High
Advisory: BIT-gulp-2021-35065
Aliases: CVE-2021-35065, GHSA-cj88-88mr-972w
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gulp-2021-35065
Type: osv

## Affected
- Bitnami: `gulp` — affected >=6.0.0 <6.0.1

## Details
The glob-parent package before 6.0.1 for Node.js allows ReDoS (regular expression denial of service) attacks against the enclosure regular expression.

## References
- https://github.com/gulpjs/glob-parent/commit/3e9f04a3b4349db7e1962d87c9a7398cda51f339
- https://github.com/gulpjs/glob-parent/pull/49
- https://security.snyk.io/vuln/SNYK-JS-GLOBPARENT-1314294
- https://security.netapp.com/advisory/ntap-20230214-0010/
- https://nvd.nist.gov/vuln/detail/CVE-2021-35065
