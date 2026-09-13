# [M] Synapse pagination Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-6qf2-7x63-mm6v
CVE: CVE-2026-45076
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-6qf2-7x63-mm6v
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.152.1

## Details
### Impact

In federated rooms, malicious homeservers can craft room events in such a way that prevents Synapse from providing full history to paginating clients.

Clients could therefore fail to display room history.

### Patches

Update to Synapse 1.152.1 or later.

### Workarounds

There are no known workarounds for this issue.

### Identifiers

- ELEMENTSEC-2025-1636

### For more information

If you have any questions or comments about this advisory, please email us at [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-6qf2-7x63-mm6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-45076
- https://github.com/element-hq/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2026-194.yaml
