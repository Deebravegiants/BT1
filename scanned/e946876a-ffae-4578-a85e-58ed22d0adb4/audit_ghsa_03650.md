# [H] Parse Server before v3.4.1 vulnerable to Denial of Service

## Summary
Severity: High
Advisory: GHSA-2479-qvv7-47qq
CVE: CVE-2019-1020012
CWE: CWE-444
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-06-13
Source: https://github.com/advisories/GHSA-2479-qvv7-47qq
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <3.4.1

## Details
### Impact

If a POST request is made to /parse/classes/_Audience (or other volatile class), any subsuquent POST requests result in an internal server error (500).


### Patches
Afflicted installations will also have to remove the offending collection from their database.

Yes, patched in 3.4.1

### Workarounds

Yes, user can apply: https://github.com/parse-community/parse-server/commit/8709daf698ea69b59268cb66f0f7cee75b52daa5

### References
Nothing other than this advisory at this time

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [parse-server](https://github.com/parse-community/parse-server)
* Email us at [security@parseplatform.org](mailto:security@parseplatform.org)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-2479-qvv7-47qq
- https://nvd.nist.gov/vuln/detail/CVE-2019-1020012
- https://github.com/advisories/GHSA-2479-qvv7-47qq
- https://github.com/parse-community/parse-server
- https://snyk.io/vuln/SNYK-JS-PARSESERVER-455635
- https://www.npmjs.com/advisories/1113
