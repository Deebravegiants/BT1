# [M] OpenClaw 2026.4.10 < 2026.4.14 - Loss of Group Tool-Policy Context in Delivery Queue Recovery

## Summary
Severity: Medium
Advisory: CVE-2026-43583
Aliases: GHSA-r77c-2cmr-7p47
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43583
Type: osv

## Details
OpenClaw versions 2026.4.10 before 2026.4.14 fail to persist session context during delivery queue recovery for media replay. Attackers can exploit recovered queued outbound media to bypass group tool policy enforcement and weaken channel media restrictions after service restart or recovery.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43583.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-r77c-2cmr-7p47
- https://nvd.nist.gov/vuln/detail/CVE-2026-43583
- https://www.vulncheck.com/advisories/openclaw-loss-of-group-tool-policy-context-in-delivery-queue-recovery
- https://github.com/openclaw/openclaw/commit/48aae82bbc19ba8b0741e61a08063eb0d1df464e
