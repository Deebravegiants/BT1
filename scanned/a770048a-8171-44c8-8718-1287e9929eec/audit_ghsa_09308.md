# [C] TYPO3 Remote Code Execution in extension "Content Element Selector" (ceselector)

## Summary
Severity: Critical
Advisory: GHSA-8x3j-439w-537c
CVE: CVE-2026-46725
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-8x3j-439w-537c
Type: github-advisory

## Affected
- Packagist: `mmc/ceselector` — affected >=6.0.0 <6.0.1
- Packagist: `mmc/ceselector` — affected >=5.0.0 <5.0.1
- Packagist: `mmc/ceselector` — affected >=4.0.0 <4.0.2
- Packagist: `mmc/ceselector` — affected >=0 <3.0.3

## Details
The TYPO3 "Content Element Selector" (ceselector) extension passes an attacker-controlled cookie directly to PHP's `unserialize()` without safely processing the input. A remote, unauthenticated attacker can supply a crafted serialized payload to trigger PHP Object Injection, leading to Remote Code Execution on the TYPO3 server. Exploitation requires the content element to be configured with `Persistent Mode: Static` in the plugin settings. This has been patched in version 3.0.3, 4.0.2, 5.0.1, and 6.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-46725
- https://bitbucket.org/thismaechler/typo3-ext-ceselector
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mmc/ceselector/CVE-2026-46725.yaml
- https://typo3.org/security/advisory/typo3-ext-sa-2026-013
