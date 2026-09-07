# [M] Cross-site scripting in json-sanitizer

## Summary
Severity: Medium
Advisory: GHSA-g8jj-899q-8x3j
CVE: CVE-2020-13973
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-g8jj-899q-8x3j
Type: github-advisory

## Affected
- Maven: `com.mikesamuel:json-sanitizer` — affected >=0 <1.2.1

## Details
OWASP json-sanitizer before 1.2.1 allows XSS. An attacker who controls a substring of the input JSON, and controls another substring adjacent to a SCRIPT element in which the output is embedded as JavaScript, may be able to confuse the HTML parser as to where the SCRIPT element ends, and cause non-script content to be interpreted as JavaScript.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13973
- https://github.com/OWASP/json-sanitizer/pull/20
