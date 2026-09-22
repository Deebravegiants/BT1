# [M] Sensitive Data Exposure in parse-server

## Summary
Severity: Medium
Advisory: GHSA-8w3j-g983-8jh5
CVE: CVE-2019-1020013
CWE: CWE-209
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-07-11
Source: https://github.com/advisories/GHSA-8w3j-g983-8jh5
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=0 <3.6.0

## Details
Versions of parse-server prior to 3.6.0 could allow an account enumeration attack via account linking.
`ParseError.ACCOUNT_ALREADY_LINKED(208)` was thrown BEFORE the AuthController checks the password and throws a `ParseError.SESSION_MISSING(206)` for Insufficient auth.  An attacker can guess ids and get information about linked accounts/email addresses.

### For more information
If you have any questions or comments about this advisory,
Open an issue in the [parse-server](https://github.com/parse-community/parse-server)
[Parse Community Vulnerability Disclosure Program](https://github.com/parse-community/parse-server/blob/master/SECURITY.md)

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-8w3j-g983-8jh5
- https://nvd.nist.gov/vuln/detail/CVE-2019-1020013
- https://github.com/parse-community/parse-server/commit/73b0f9a339b81f5d757725dc557955a7b670a3ec
- https://github.com/advisories/GHSA-8w3j-g983-8jh5
- https://snyk.io/vuln/SNYK-JS-PARSESERVER-455637
- https://www.npmjs.com/advisories/1114
- https://www.owasp.org/index.php/Testing_for_User_Enumeration_and_Guessable_User_Account_(OWASP-AT-002)#Description_of_the_Issue
