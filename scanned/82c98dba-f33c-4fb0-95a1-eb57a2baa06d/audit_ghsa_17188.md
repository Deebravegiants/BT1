# [H] CodeIgniter4 DoS Vulnerability

## Summary
Severity: High
Advisory: GHSA-39fp-mqmm-gxj6
CVE: CVE-2024-29904
CWE: CWE-674, CWE-835
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-29
Source: https://github.com/advisories/GHSA-39fp-mqmm-gxj6
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.4.7

## Details
### Impact
A vulnerability was found in the Language class that allowed DoS attacks. This vulnerability can be exploited by an attacker to consume a large amount of memory on the server.

### Patches
Upgrade to v4.4.7 or later. See [upgrading guide](https://codeigniter4.github.io/userguide/installation/upgrade_447.html).

### Workarounds
- Disabling Auto Routing prevents a known attack vector in the framework.
- Do not pass invalid values to the `lang()` function or `Language` class.

### References
- https://codeigniter4.github.io/userguide/outgoing/localization.html#language-localization
- https://codeigniter4.github.io/userguide/general/common_functions.html#lang

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-39fp-mqmm-gxj6
- https://nvd.nist.gov/vuln/detail/CVE-2024-29904
- https://github.com/codeigniter4/CodeIgniter4/commit/fa851acbae7ae4c5a97f8f38ae87aa0822a334c0
- https://github.com/codeigniter4/CodeIgniter4
