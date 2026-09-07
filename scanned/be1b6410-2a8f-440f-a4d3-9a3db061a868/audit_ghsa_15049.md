# [H] network Arbitrary Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-vvh2-82c7-ppfg
CVE: CVE-2024-21488
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-vvh2-82c7-ppfg
Type: github-advisory

## Affected
- npm: `network` — affected >=0 <0.7.0

## Details
Versions of the package network before 0.7.0 are vulnerable to Arbitrary Command Injection due to use of the `child_process` exec function without input sanitization. If (attacker-controlled) user input is given to the `mac_address_for` function of the package, it is possible for an attacker to execute arbitrary commands on the operating system that this package is being run on.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21488
- https://github.com/tomas/network/commit/5599ed6d6ff1571a5ccadea775430c131f381de7
- https://github.com/tomas/network/commit/6ec8713580938ab4666df2f2d0f3399891ed2ad7
- https://github.com/tomas/network/commit/72c523265940fe279eb0050d441522628f8988e5
- https://gist.github.com/icemonster/282ab98fb68fc22aac7c576538f6369c
- https://github.com/tomas/network
- https://security.snyk.io/vuln/SNYK-JS-NETWORK-6184371
