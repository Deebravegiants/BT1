# [M] Regular expression Denial of Service in @progfay/scrapbox-parser

## Summary
Severity: Medium
Advisory: GHSA-9fhw-r42p-5c7r
CVE: CVE-2021-27405
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-03-01
Source: https://github.com/advisories/GHSA-9fhw-r42p-5c7r
Type: github-advisory

## Affected
- npm: `@progfay/scrapbox-parser` — affected >=0 <6.0.3
- npm: `@progfay/scrapbox-parser` — affected >=7.0.0 <7.0.2

## Details
### Impact

A [Regular expression Denial of Service](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) flaw was found in the @progfay/scrapbox-parser package before 6.0.3, 7.0.2 for Node.js.
The attacker that is able to be parsed a specially crafted text may cause the application to consume an excessive amount of CPU.

### Patches

Upgrade to version 6.0.3, 7.0.2 or later.

### Workarounds

Avoid to parse text with a lot of `[` chars.

### References

* https://github.com/progfay/scrapbox-parser/pull/519
* https://github.com/progfay/scrapbox-parser/pull/539
* https://github.com/progfay/scrapbox-parser/pull/540
* https://cve.mitre.org/cgi-bin/cvename.cgi?name=2021-27405
* https://snyk.io/vuln/SNYK-JS-PROGFAYSCRAPBOXPARSER-1076803

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [github.com/progfay/scrapbox-parser](https://github.com/progfay/scrapbox-parser/issues)

## References
- https://github.com/progfay/scrapbox-parser/security/advisories/GHSA-9fhw-r42p-5c7r
- https://nvd.nist.gov/vuln/detail/CVE-2021-27405
- https://github.com/progfay/scrapbox-parser/pull/519
- https://github.com/progfay/scrapbox-parser/pull/539
- https://github.com/progfay/scrapbox-parser/pull/540
- https://security.netapp.com/advisory/ntap-20210326-0002
