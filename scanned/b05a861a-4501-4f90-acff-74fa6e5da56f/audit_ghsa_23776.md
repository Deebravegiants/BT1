# [M] Lift Sensitive Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-jf9v-fxfq-wm76
CVE: CVE-2013-3300
CWE: CWE-119
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jf9v-fxfq-wm76
Type: github-advisory

## Affected
- Maven: `net.liftweb:lift-webkit` — affected >=0
- Maven: `net.liftweb:lift-webkit_2.7.7` — affected >=0
- Maven: `net.liftweb:lift-webkit_2.8.0` — affected >=0
- Maven: `net.liftweb:lift-webkit_2.8.1` — affected >=0
- Maven: `net.liftweb:lift-webkit_2.8.2` — affected >=0
- Maven: `net.liftweb:lift-webkit_2.9.0` — affected >=0
- Maven: `net.liftweb:lift-webkit_2.9.0-1` — affected >=0
- Maven: `net.liftweb:lift-webkit_2.9.1` — affected >=0 <2.5

## Details
The JsonParser class in json/JsonParser.scala in Lift before 2.5 interprets a certain end-index value as a length value, which allows remote authenticated users to obtain sensitive information from other users' sessions via invalid input data containing a < (less than) character.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-3300
- https://github.com/lift/framework/commit/099d9c86cf6d81f4953957add478ab699946e601
- https://github.com/lift/framework
- http://blog.addepar.com/2013/07/an-atypical-web-vulnerability.html
