# [H] Synapse CPU starvation (Denial of Service)

## Summary
Severity: High
Advisory: GHSA-8q93-326v-3m7g
CVE: CVE-2026-45078
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-8q93-326v-3m7g
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.152.1

## Details
### Impact

Local authenticated users can cause Synapse to starve other requests of CPU and lead to other requests failing, causing other users to be denied service.

Homeservers that trust all their local users are not at risk.

### Patches

Update to Synapse 1.152.1 or later.

### Workarounds

If Synapse is deployed behind a reverse proxy, the reverse proxy could be configured to limit the rate of user requests,
preventing or increasing the difficulty of the attack.

### Identifiers

- ELEMENTSEC-2026-1706

### For more information

If you have any questions or comments about this advisory, please email us at [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-8q93-326v-3m7g
- https://nvd.nist.gov/vuln/detail/CVE-2026-45078
- https://github.com/element-hq/synapse/issues/19394
- https://github.com/element-hq/synapse/commit/3f58bc50dfba5768ee43ce48c5e74c25ba0b078a
- https://github.com/element-hq/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2026-191.yaml
