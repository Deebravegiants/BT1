# [H] bson-objectid contains Improper input validation

## Summary
Severity: High
Advisory: GHSA-p84x-5xx8-hff9
CVE: CVE-2019-19729
CWE: CWE-20, CWE-670
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p84x-5xx8-hff9
Type: github-advisory

## Affected
- npm: `bson-objectid` — affected >=0

## Details
An issue was discovered in the BSON ObjectID (aka bson-objectid) package 1.3.0 for Node.js. ObjectID() allows an attacker to generate a malformed objectid by inserting an additional property to the user-input, because bson-objectid will return early if it `detects _bsontype==ObjectID` in the user-input object. As a result, objects in arbitrary forms can bypass formatting if they have a valid bsontype.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19729
- https://github.com/williamkapke/bson-objectid/issues/30
- https://github.com/cabinjs/bson-objectid
- https://www.npmjs.com/package/bson-objectid
