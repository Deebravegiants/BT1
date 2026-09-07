# [M] insane vulnerable to Regular Expression Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-w455-mfq9-hf74
CVE: CVE-2020-26303
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-26
Source: https://github.com/advisories/GHSA-w455-mfq9-hf74
Type: github-advisory

## Affected
- npm: `insane` — affected >=0

## Details
insane is a whitelist-oriented HTML sanitizer. Versions 2.6.2 and prior contain one or more regular expressions that are vulnerable to Regular Expression Denial of Service (ReDoS). As of time of publication, no known patches are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26303
- https://github.com/bevacqua/insane/issues/19
- https://github.com/bevacqua/insane
- https://securitylab.github.com/advisories/GHSL-2020-289-redos-insane
