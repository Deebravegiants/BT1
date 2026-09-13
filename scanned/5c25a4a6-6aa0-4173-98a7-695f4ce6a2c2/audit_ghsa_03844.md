# [C] Improper Input Validation in Automattic Mongoose

## Summary
Severity: Critical
Advisory: GHSA-8687-vv9j-hgph
CVE: CVE-2019-17426
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2019-10-22
Source: https://github.com/advisories/GHSA-8687-vv9j-hgph
Type: github-advisory

## Affected
- npm: `mongoose` — affected >=5.0.0 <5.7.5
- npm: `mongoose` — affected >=0 <4.13.21

## Details
Automattic Mongoose through 5.7.4 allows attackers to bypass access control (in some applications) because any query object with a `_bsontype` attribute is ignored. For example, adding `"_bsontype":"a"` can sometimes interfere with a query filter. NOTE: this CVE is about Mongoose's failure to work around this _bsontype special case that exists in older versions of the bson parser (aka the mongodb/js-bson project).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17426
- https://github.com/Automattic/mongoose/issues/8222
- https://github.com/Automattic/mongoose/commit/f3eca5b94d822225c04e96cbeed9f095afb3c31c
- https://github.com/Automattic/mongoose/commit/f88eb2524b65a68ff893c90a03c04f0913c1913e
- https://github.com/Automattic/mongoose
- https://github.com/Automattic/mongoose/commits/4.13.21
- https://github.com/Automattic/mongoose/releases/tag/4.13.21
