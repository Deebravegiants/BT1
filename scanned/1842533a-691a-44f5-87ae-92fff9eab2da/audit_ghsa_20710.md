# [M] uri-template-lite Regular Expression Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-chw2-6c7r-37p7
CVE: CVE-2021-43309
CWE: CWE-1333, CWE-697
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-25
Source: https://github.com/advisories/GHSA-chw2-6c7r-37p7
Type: github-advisory

## Affected
- npm: `uri-template-lite` — affected >=0 <22.9.0

## Details
An exponential ReDoS (Regular Expression Denial of Service) can be triggered in the uri-template-lite npm package, when an attacker is able to supply arbitrary input to the "URI.expand" method.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-43309
- https://github.com/litejs/uri-template-lite/commit/cbeec2b2a275d819fb534137a155df14729706f8
- https://github.com/litejs/uri-template-lite
- https://github.com/litejs/uri-template-lite/commits/v22.9.0
- https://research.jfrog.com/vulnerabilities/uri-template-lite-redos-xray-211351
