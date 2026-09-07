# [H] pacote is vulnerable to Denial of Service (DoS) via the addGitSha function

## Summary
Severity: High
Advisory: GHSA-w4pp-8pjf-rmxw
CVE: CVE-2026-9496
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-w4pp-8pjf-rmxw
Type: github-advisory

## Affected
- npm: `pacote` — affected >=11.2.7 <21.5.1

## Details
Versions of the package pacote from 11.2.7 are vulnerable to Denial of Service (DoS) via the addGitSha function. An attacker can exploit this vulnerability by supplying a specially crafted spec.rawSpec value that triggers the function’s regex replacement and string-manipulation logic, causing excessive CPU consumption and potentially stalling or crashing the process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-9496
- https://github.com/npm/pacote/commit/627a7dc1a214d857472a13b48e42559c75288c9e
- https://github.com/npm/pacote/commit/ce804fb1647fe1699b2f87efd01ea9f4efed8508
- https://github.com/npm/pacote
- https://github.com/npm/pacote/blob/9d7459440826ab4cf962ef98d8f3fd0c4d464b5c/lib/util/add-git-sha.js%23L2C1-L13C2
- https://github.com/npm/pacote/releases/tag/v21.5.1
- https://github.com/npm/pacote/releases/tag/v22.0.0
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-16874025
- https://security.snyk.io/vuln/SNYK-JS-PACOTE-8225084
