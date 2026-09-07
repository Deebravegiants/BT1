# [M] teler-waf subject to Bypass of Common Web Attack Threat Rule with HTML Entities Payload

## Summary
Severity: Medium
Advisory: GHSA-9f95-hhg4-pg4f
CVE: CVE-2023-26046
CWE: CWE-79, CWE-80
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-9f95-hhg4-pg4f
Type: github-advisory

## Affected
- Go: `github.com/kitabisa/teler-waf` — affected >=0 <0.1.1

## Details
### Description

teler-waf is a Go HTTP middleware that provides teler IDS functionality to protect against web-based attacks. Versions prior to v0.1.1 are vulnerable to bypassing common web attack rules when a specific HTML entities payload is used. This vulnerability allows an attacker to execute arbitrary JavaScript code on the victim's browser and compromise the security of the web application. The vulnerability exists due to teler-waf failure to properly sanitize and filter HTML entities in user input.

### Impact

An attacker can exploit this vulnerability to bypass common web attack threat rules in teler-waf and launch cross-site scripting (XSS) attacks. The attacker can execute arbitrary JavaScript code on the victim's browser and steal sensitive information, such as login credentials and session tokens, or take control of the victim's browser and perform malicious actions.

### Patches

Version [v0.1.1](https://github.com/kitabisa/teler-waf/releases/tag/v0.1.1) includes a patch for this vulnerability.

### Workarounds

We advised updating their installations to version `v0.1.1` and frontwards immediately.

## References
- https://github.com/kitabisa/teler-waf/security/advisories/GHSA-9f95-hhg4-pg4f
- https://nvd.nist.gov/vuln/detail/CVE-2023-26046
- https://github.com/kitabisa/teler-waf/commit/d1d49cfddfa3ec2adad962870f14b85cd1aaf739
- https://github.com/kitabisa/teler-waf
- https://github.com/kitabisa/teler-waf/compare/v0.1.0...v0.1.1
- https://github.com/kitabisa/teler-waf/releases/tag/v0.1.1
- https://pkg.go.dev/vuln/GO-2023-1597
