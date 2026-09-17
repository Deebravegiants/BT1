# [H] Sparkle Signing Checks Bypass

## Summary
Severity: High
Advisory: GHSA-wc9m-r3v6-9p5h
CVE: CVE-2025-0509
CWE: CWE-552
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:A/AC:H/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-04
Source: https://github.com/advisories/GHSA-wc9m-r3v6-9p5h
Type: github-advisory

## Affected
- SwiftURL: `github.com/sparkle-project/Sparkle` — affected >=0 <2.6.4

## Details
A security issue was found in Sparkle before version 2.6.4. An attacker can replace an existing signed update with another payload, bypassing Sparkle’s (Ed)DSA signing checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-0509
- https://github.com/sparkle-project/Sparkle/pull/2550
- https://github.com/sparkle-project/Sparkle
- https://security.netapp.com/advisory/ntap-20250124-0008
- https://sparkle-project.org/documentation/security-and-reliability
