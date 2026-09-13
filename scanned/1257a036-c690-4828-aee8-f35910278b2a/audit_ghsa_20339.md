# [H] OS Command Injection in lifion-verify-deps

## Summary
Severity: High
Advisory: GHSA-rphm-c8gw-3r38
CVE: CVE-2021-34078
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-03
Source: https://github.com/advisories/GHSA-rphm-c8gw-3r38
Type: github-advisory

## Affected
- npm: `lifion-verify-deps` — affected >=0 <1.2.0

## Details
lifion-verify-dependencies through 1.1.0 is vulnerable to OS command injection via a crafted dependency name on the scanned project's package.json file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34078
- https://github.com/lifion/lifion-verify-deps/commit/be1133d5b78e3caa0004fa60207013dca4e1bf38
- https://advisory.checkmarx.net/advisory/CX-2021-4785
- https://github.com/lifion/lifion-verify-deps
