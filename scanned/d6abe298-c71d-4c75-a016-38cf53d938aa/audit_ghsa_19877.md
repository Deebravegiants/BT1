# [H] Synapse vulnerable to federation denial of service via malformed events

## Summary
Severity: High
Advisory: GHSA-v56r-hwv5-mxg6
CVE: CVE-2025-30355
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-03-27
Source: https://github.com/advisories/GHSA-v56r-hwv5-mxg6
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.127.1

## Details
### Impact
A malicious server can craft events with a `depth` outside the integer range allowed by Canonical JSON. When such an event is received by Synapse version up to 1.127.0, it prevents it from federating with other servers. The vulnerability has been exploited in the wild.

### Patches
Fixed in Synapse v1.127.1.

### Workarounds
Closed federation environments of trusted servers or non-federating installations are not affected.

### For more information

If you have any questions or comments about this advisory, please email us at [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-v56r-hwv5-mxg6
- https://nvd.nist.gov/vuln/detail/CVE-2025-30355
- https://github.com/element-hq/synapse/commit/2277df2a1eb685f85040ef98fa21d41aa4cdd389
- https://github.com/element-hq/synapse
- https://github.com/element-hq/synapse/releases/tag/v1.127.1
