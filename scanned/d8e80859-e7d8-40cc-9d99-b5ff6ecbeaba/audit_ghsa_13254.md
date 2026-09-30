# [M] Electron vulnerable to out-of-package code execution when launched with arbitrary cwd

## Summary
Severity: Medium
Advisory: GHSA-7x97-j373-85x5
CVE: CVE-2023-39956
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2023-09-06
Source: https://github.com/advisories/GHSA-7x97-j373-85x5
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <22.3.19
- npm: `electron` — affected >=23.0.0-alpha.1 <23.3.13
- npm: `electron` — affected >=24.0.0-alpha.1 <24.7.1
- npm: `electron` — affected >=25.0.0-alpha.1 <25.5.0
- npm: `electron` — affected >=26.0.0-alpha.1 <26.0.0-beta.13

## Details
### Impact
Apps that are launched as command line executables are impacted.  E.g. if your app exposes itself in the path as `myapp --help`

Specifically this issue can only be exploited if the following conditions are met:
* Your app is launched with an attacker-controlled working directory
* The attacker has the ability to write files to that working directory

This makes the risk quite low, in fact normally issues of this kind are considered outside of our threat model as similar to Chromium we exclude [Physically Local Attacks](https://github.com/electron/electron/security/advisories/GHSA-7x97-j373-85x5#:~:text=Physically%20Local%20Attacks) but given the ability for this issue to bypass certain protections like ASAR Integrity it is being treated with higher importance.  Please bear this in mind when reporting similar issues in the future.

### Workarounds
There are no app side workarounds, you must update to a patched version of Electron.

### Fixed Versions
* `26.0.0-beta.13`
* `25.5.0`
* `24.7.1`
* `23.3.13`
* `22.3.19`

### For more information
If you have any questions or comments about this advisory, email us at [security@electronjs.org](mailto:security@electronjs.org)

## References
- https://github.com/electron/electron/security/advisories/GHSA-7x97-j373-85x5
- https://nvd.nist.gov/vuln/detail/CVE-2023-39956
- https://github.com/electron/electron
