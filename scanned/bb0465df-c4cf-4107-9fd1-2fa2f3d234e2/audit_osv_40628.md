# [H] OpenClaw < 2026.5.3 - Mutable Display Name Binding in Zalo allowFrom Policy

## Summary
Severity: High
Advisory: CVE-2026-53857
Aliases: GHSA-8c59-hr4w-qg69
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-16
Source: https://osv.dev/vulnerability/CVE-2026-53857
Type: osv

## Details
OpenClaw before 2026.5.3 contains a policy enforcement vulnerability where Zalo contacts with mutable display metadata could match allowFrom policy entries through display name changes. Attackers with mutable display names could receive agent responses intended for different Zalo identities when the feature is enabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53857.json
- https://github.com/openclaw/openclaw/security/advisories/GHSA-8c59-hr4w-qg69
- https://nvd.nist.gov/vuln/detail/CVE-2026-53857
- https://www.vulncheck.com/advisories/openclaw-mutable-display-name-binding-in-zalo-allowfrom-policy
- https://github.com/openclaw/openclaw
