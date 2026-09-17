# [H] knowns before 0.30.0 Authorization Bypass via Misclassified Code Actions

## Summary
Severity: High
Advisory: CVE-2026-86544
Aliases: GHSA-w323-3wpx-f7g5
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-07
Source: https://osv.dev/vulnerability/CVE-2026-86544
Type: osv

## Details
knowns versions before 0.30.0 contain an authorization bypass vulnerability where mutating code actions are incorrectly classified as read-only operations. Attackers with read-restricted sessions can exploit code.replace to modify permission configurations and escalate privileges on subsequent calls.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86544.json
- https://github.com/knowns-dev/knowns/releases/tag/v0.30.0
- https://github.com/knowns-dev/knowns/security/advisories/GHSA-w323-3wpx-f7g5
- https://nvd.nist.gov/vuln/detail/CVE-2026-86544
- https://www.vulncheck.com/advisories/knowns-before-0.30.0-authorization-bypass-via-misclassified-code-actions
- https://github.com/knowns-dev/knowns/commit/a2c98fc5c313463576c9348beeec6a74ddd7333b
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/permissions/guard.go#L44-L60
- https://github.com/knowns-dev/knowns/blob/v0.29.1/internal/permissions/registry.go#L99-L140
