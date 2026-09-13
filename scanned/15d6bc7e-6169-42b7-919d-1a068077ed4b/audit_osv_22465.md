# [H] CVE-2022-30288

## Summary
Severity: High
Advisory: CVE-2022-30288
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-04
Source: https://osv.dev/vulnerability/CVE-2022-30288
Type: osv

## Details
Agoo before 2.14.3 does not reject GraphQL fragment spreads that form cycles, leading to an application crash. NOTE: the vendor has disputed this on the grounds that it is not the server's responsibility to "enforce all the various ways a developer could write code with logic errors.

## References
- https://github.com/nicholasaleks/graphql-threat-matrix/blob/master/implementations/agoo.md
- https://spec.graphql.org/October2021/#sec-Fragment-spreads-must-not-form-cycles
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/30xxx/CVE-2022-30288.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-30288
- https://github.com/ohler55/agoo/issues/109
