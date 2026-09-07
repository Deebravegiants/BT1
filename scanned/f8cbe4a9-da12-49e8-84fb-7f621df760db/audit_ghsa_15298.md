# [C] CasaOS Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-92vc-4fcw-g68q
CVE: CVE-2023-37469
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-92vc-4fcw-g68q
Type: github-advisory

## Affected
- Go: `github.com/IceWhaleTech/CasaOS` — affected >=0 <0.4.4

## Details
CasaOS is an open-source personal cloud system. Prior to version 0.4.4, if an authenticated user using CasaOS is able to successfully connect to a controlled SMB server, they are able to execute arbitrary commands. Version 0.4.4 contains a patch for the issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-37469
- https://github.com/github/pe-security-lab/issues/1871
- https://github.com/IceWhaleTech/CasaOS/commit/af440eac5563644854ff33f72041e52d3fd1f47c
- https://github.com/IceWhaleTech/CasaOS
- https://github.com/IceWhaleTech/CasaOS/blob/96e92842357230098c771bc41fd3baf46189b859/route/v1/samba.go#L121
- https://github.com/IceWhaleTech/CasaOS/blob/96e92842357230098c771bc41fd3baf46189b859/service/connections.go#L58
- https://github.com/IceWhaleTech/CasaOS/releases/tag/v0.4.4
- https://securitylab.github.com/advisories/GHSL-2022-119_CasaOS
