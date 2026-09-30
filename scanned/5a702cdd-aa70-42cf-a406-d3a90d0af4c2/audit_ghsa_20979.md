# [M] parse-url parses http URLs incorrectly, making it vulnerable to host name spoofing

## Summary
Severity: Medium
Advisory: GHSA-pqw5-jmp5-px4v
CVE: CVE-2022-3224
CWE: CWE-115
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-pqw5-jmp5-px4v
Type: github-advisory

## Affected
- npm: `parse-url` — affected >=0 <8.1.0

## Details
parse-url prior to 8.1.0 is vulnerable to Misinterpretation of Input. parse-url parses certain http or https URLs incorrectly, identifying the URL's protocol as ssh. It may also parse the host name incorrectly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3224
- https://github.com/ionicabizau/parse-url/commit/9cacf38de02db0fb1358bd6ec04543e523cd6a8e
- https://github.com/ionicabizau/parse-url
- https://huntr.dev/bounties/3587a567-7fcd-4702-b7c9-d9ca565e3c62
