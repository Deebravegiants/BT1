# [H] Machine-In-The-Middle in airtable

## Summary
Severity: High
Advisory: GHSA-jrj9-5qp6-2v8q
Ecosystem: npm
Published: 2020-09-03
Source: https://github.com/advisories/GHSA-jrj9-5qp6-2v8q
Type: github-advisory

## Affected
- npm: `airtable` — affected >=0.1.19 <0.7.2

## Details
Affected versions of `airtable` are vulnerable to Machine-In-The-Middle. The package has SSL certificate validation disabled by default unintentionally. This may allow attackers in a privileged network position to decrypt intercepted traffic.


## Recommendation

Upgrade to version 0.7.2 or later.

## References
- https://www.npmjs.com/advisories/1305
