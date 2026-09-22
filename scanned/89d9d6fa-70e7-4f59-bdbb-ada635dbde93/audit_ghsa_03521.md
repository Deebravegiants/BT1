# [M] Denial of service attack via .well-known lookups

## Summary
Severity: Medium
Advisory: GHSA-2hwx-mjrm-v3g8
CVE: CVE-2021-21274
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-03-01
Source: https://github.com/advisories/GHSA-2hwx-mjrm-v3g8
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0.99.0 <1.25.0

## Details
### Impact
A malicious homeserver could redirect requests to their .well-known file to a large file. This can lead to a denial of service attack where homeservers will consume significantly more resources when requesting the .well-known file of a malicious homeserver.

This affects any server which accepts federation requests from untrusted servers.

### Patches
Issue is resolved by #8950. A bug not affecting the security aspects of this was fixed in #9108.

### Workarounds
The `federation_domain_whitelist` setting can be used to restrict the homeservers communicated with over federation.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-2hwx-mjrm-v3g8
- https://nvd.nist.gov/vuln/detail/CVE-2021-21274
- https://github.com/matrix-org/synapse/pull/8950
- https://github.com/matrix-org/synapse/commit/ff5c4da1289cb5e097902b3e55b771be342c29d6
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v1.25.0
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2021-132.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TNNAJOZNMVMXM6AS7RFFKB4QLUJ4IFEY
