# [M] OpenClaw 2026.6.6 < 2026.6.9 Authorization Bypass via Message Mutations

## Summary
Severity: Medium
Advisory: CVE-2026-62191
Aliases: GHSA-v7hx-r36p-f68m
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62191
Type: osv

## Details
OpenClaw versions 2026.6.6 before 2026.6.9 contain an authorization bypass vulnerability in message mutation handling that allows lower-trust callers to perform actions requiring stronger authorization checks. Attackers can exploit misconfigured input paths to skip requester authorization and execute privileged operations when the affected feature is enabled and reachable.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62191.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-v7hx-r36p-f68m
- https://nvd.nist.gov/vuln/detail/CVE-2026-62191
- https://www.vulncheck.com/advisories/openclaw-authorization-bypass-via-message-mutations
- https://github.com/openclaw/openclaw
