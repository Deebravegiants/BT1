# [M] lorawan-stack Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5fwq-9x7j-2qpg
CVE: CVE-2023-26494
CWE: CWE-601
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-5fwq-9x7j-2qpg
Type: github-advisory

## Affected
- Go: `go.thethings.network/lorawan-stack/v3` — affected >=0 <3.24.1

## Details
lorawan-stack is an open source LoRaWAN network server. Prior to version 3.24.1, an open redirect exists on the login page of the lorawan stack server, allowing an attacker to supply a user controlled redirect upon sign in. This issue may allows malicious actors to phish users, as users assume they were redirected to the homepage on login. Version 3.24.1 contains a fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26494
- https://github.com/TheThingsNetwork/lorawan-stack/commit/f06776028bdb3994847fc6067613dc61a2b3559e
- https://github.com/TheThingsNetwork/lorawan-stack
- https://github.com/TheThingsNetwork/lorawan-stack/blob/ecdef730f176c02f7c9afce98b0457ae64de5bfc/pkg/webui/account/views/login/index.js#L90-L90
- https://github.com/TheThingsNetwork/lorawan-stack/blob/ecdef730f176c02f7c9afce98b0457ae64de5bfc/pkg/webui/account/views/token-login/index.js#L74-L74
- https://github.com/TheThingsNetwork/lorawan-stack/releases/tag/v3.24.1
- https://securitylab.github.com/advisories
- https://securitylab.github.com/advisories/GHSL-2022-138_lorawan-stack
