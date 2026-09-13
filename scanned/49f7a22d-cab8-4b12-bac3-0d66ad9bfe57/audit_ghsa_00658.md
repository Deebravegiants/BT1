# [H] Denial of service attack via incorrect parameters in Matrix Synapse

## Summary
Severity: High
Advisory: GHSA-hxmp-pqch-c8mm
CVE: CVE-2020-26257
CWE: CWE-400, CWE-74, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-12-09
Source: https://github.com/advisories/GHSA-hxmp-pqch-c8mm
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.23.1

## Details
### Impact

A malicious or poorly-implemented homeserver can inject malformed events into a room by specifying a different room id in the path of a `/send_join`, `/send_leave`, `/invite` or `/exchange_third_party_invite` request.

This can lead to a denial of service in which future events will not be correctly sent to other servers over federation.

This affects any server which accepts federation requests from untrusted servers.

### Patches

Issue is resolved by https://github.com/matrix-org/synapse/pull/8776.

### Workarounds

Homeserver administrators could limit access to the federation API to trusted servers (for example via `federation_domain_whitelist`).

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-hxmp-pqch-c8mm
- https://nvd.nist.gov/vuln/detail/CVE-2020-26257
- https://github.com/matrix-org/synapse/pull/8776
- https://github.com/matrix-org/synapse/commit/3ce2f303f15f6ac3dc352298972dc6e04d9b7a8b
- https://github.com/matrix-org/synapse/blob/develop/CHANGES.md#synapse-1231-2020-12-09
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2020-236.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DBTIU3ZNBFWZ56V4X7JIAD33V5H2GOMC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QR4MMYZKX5N5GYGH4H5LBUUC5TLAFHI7
