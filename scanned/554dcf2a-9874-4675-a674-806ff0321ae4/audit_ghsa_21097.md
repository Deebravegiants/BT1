# [C] SQL injection in typeORM

## Summary
Severity: Critical
Advisory: GHSA-fx4w-v43j-vc45
CVE: CVE-2022-33171
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-05
Source: https://github.com/advisories/GHSA-fx4w-v43j-vc45
Type: github-advisory

## Affected
- npm: `typeorm` — affected >=0 <0.3.0

## Details
The findOne function in TypeORM before 0.3.0 can either be supplied with a string or a FindOneOptions object. When input to the function is a user-controlled parsed JSON object, supplying a crafted FindOneOptions instead of an id string leads to SQL injection. NOTE: the vendor's position is that the user's application is responsible for input validation.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-33171
- https://github.com/typeorm/typeorm/compare/0.2.45...0.3.0
- https://seclists.org/fulldisclosure/2022/Jun/51
- http://packetstormsecurity.com/files/168096/TypeORM-0.3.7-Information-Disclosure.html
- http://seclists.org/fulldisclosure/2022/Aug/7
