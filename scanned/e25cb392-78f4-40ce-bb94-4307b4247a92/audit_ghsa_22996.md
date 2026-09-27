# [C] Improper Input Validation in IpMatcher

## Summary
Severity: Critical
Advisory: GHSA-qj93-37f5-mr29
CVE: CVE-2021-33318
CWE: CWE-20, CWE-704
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qj93-37f5-mr29
Type: github-advisory

## Affected
- NuGet: `IpMatcher` — affected >=0 <1.0.4.2

## Details
An Input Validation Vulnerability exists in Joel Christner .NET C# packages WatsonWebserver, IpMatcher 1.0.4.1 and below (IpMatcher) and 4.1.3 and below (WatsonWebserver) due to insufficient validation of input IP addresses and netmasks against the internal Matcher list of IP addresses and subnets.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-33318
- https://github.com/jchristn/IpMatcher/commit/81d77c2f33aa912dbd032b34b9e184fc6e041d89
- https://github.com/jchristn/IpMatcher
- https://github.com/jchristn/WatsonWebserver
- https://github.com/kaoudis/advisories/blob/main/0-2021.md
