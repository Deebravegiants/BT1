# [M] n8n's domain allowlist bypass enables credential exfiltration

## Summary
Severity: Medium
Advisory: GHSA-2xcx-75h9-vr9h
CVE: CVE-2026-25631
CWE: CWE-20, CWE-522
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-2xcx-75h9-vr9h
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.121.0

## Details
## Impact

A vulnerability in the HTTP Request node's credential domain validation allowed an authenticated attacker to send requests with credentials to unintended domains, potentially leading to credential exfiltration.

This only might affect user who have credentials that use wildcard domain patterns (e.g., `*.example.com`) in the "Allowed domains" setting.

## Patches

This issue is fixed in version 1.121.0 and later. All users are strongly encouraged to upgrade.

## Workarounds
Until projects can upgrade:

- Replace wildcard domain patterns with explicit domain listings in HTTP Request credentials
- Review and restrict workflow creation/modification permissions to trusted users only
- Audit existing workflows using HTTP Request nodes with domain-restricted credentials

---
n8n has adopted CVSS 4.0 as primary score for all security advisories. CVSS 3.1 vector strings are provided for backward compatibility.

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-2xcx-75h9-vr9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-25631
- https://github.com/n8n-io/n8n
