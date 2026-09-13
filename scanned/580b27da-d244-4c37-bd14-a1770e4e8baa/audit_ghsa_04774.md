# [H] launch-editor vulnerable to command injection via the crafted request on Windows

## Summary
Severity: High
Advisory: GHSA-c27g-q93r-2cwf
CVE: CVE-2024-52011
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-c27g-q93r-2cwf
Type: github-advisory

## Affected
- npm: `launch-editor` — affected >=0 <2.9.0
- npm: `vite` — affected >=0 <5.4.9

## Details
### Summary
Due to the insufficient sanitization of the `file` argument in the `launchEditor`, an attacker can execute arbitrary commands on Windows by supplying a filename that contains special characters.

### Impact
If the following conditions are met, an attacker can execute arbitrary commands on the computer that is using the `launch-editor`:

- An attacker can place a file with the malicious filename
- An attacker can call the `launchEditor` method with the `file` argument controlled
- The `launch-editor` package is running on Windows

For example, some development server using this package satisfy these conditions, as a malicious website might be able to force the downloading of a file and the path of that file is predictable.

### Patch
This issue has been fixed in the `launch-editor` version 2.9.0 ([commit](https://github.com/vitejs/launch-editor/commit/971291e8a6a91226e1616c5c0ec85423d2d50a5e)).

## References
- https://github.com/vitejs/launch-editor/security/advisories/GHSA-c27g-q93r-2cwf
- https://github.com/yyx990803/launch-editor/security/advisories/GHSA-c27g-q93r-2cwf
- https://nvd.nist.gov/vuln/detail/CVE-2024-52011
- https://github.com/vitejs/launch-editor/commit/971291e8a6a91226e1616c5c0ec85423d2d50a5e
- https://github.com/vitejs/launch-editor
