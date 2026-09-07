# [M] Project Wonder WebObjects vulnerable to Arbitrary HTTP Header Injection and Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-xv7r-9vq4-9wrq
CVE: CVE-2022-37724
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-15
Source: https://github.com/advisories/GHSA-xv7r-9vq4-9wrq
Type: github-advisory

## Affected
- Maven: `wonder:wonder` — affected >=1.0

## Details
Project Wonder WebObjects 1.0 through 7.3 is vulnerable to Arbitrary HTTP Header injection and URL- or Header-based XSS reflection in all web-server adaptor interfaces. A patch for this issue is available at commit number b0d2d74f13203268ea254b02552600850f28014b.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37724
- https://github.com/wocommunity/wonder/pull/992
- https://github.com/wocommunity/wonder/commit/b0d2d74f13203268ea254b02552600850f28014b
- https://github.com/wocommunity/wonder
- https://xmit.xyz/security/webobjects-url-tomfoolery
