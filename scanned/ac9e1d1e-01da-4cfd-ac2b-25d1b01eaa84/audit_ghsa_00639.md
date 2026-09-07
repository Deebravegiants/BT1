# [H] Electron protocol handler browser vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-fjqr-fx3f-g4rv
CVE: CVE-2018-1000118
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-03-26
Source: https://github.com/advisories/GHSA-fjqr-fx3f-g4rv
Type: github-advisory

## Affected
- npm: `electron` — affected >=0 <1.8.2-beta5

## Details
Github Electron version Electron 1.8.2-beta.4 and earlier contains a Command Injection vulnerability in Protocol Handler that can result in command execute. This attack appear to be exploitable via the victim opening an electron protocol handler in their browser. This vulnerability appears to have been fixed in Electron 1.8.2-beta.5. This issue is due to an incomplete fix for CVE-2018-1000006, specifically the black list used was not case insensitive allowing an attacker to potentially bypass it.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000118
- https://github.com/electron/electron/commit/ce361a12e355f9e1e99c989f1ea056c9e502dbe7
- https://electronjs.org/releases#1.8.2-beta.5
- https://github.com/advisories/GHSA-fjqr-fx3f-g4rv
