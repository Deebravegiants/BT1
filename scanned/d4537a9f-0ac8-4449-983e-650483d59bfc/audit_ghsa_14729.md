# [M] Synapse's unauthenticated writes to the media repository allow planting of problematic content

## Summary
Severity: Medium
Advisory: GHSA-gjgr-7834-rhxr
CVE: CVE-2024-37303
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-gjgr-7834-rhxr
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.106

## Details
### Impact

Synapse before version 1.106 allows, by design, unauthenticated remote participants to trigger a download and caching of remote media from a remote homeserver to the local media repository. Such content then also becomes available for download from the local homeserver in an unauthenticated way. The implication is that unauthenticated remote adversaries can use this functionality to plant problematic content into the media repository.

### Patches

Synapse 1.106 introduces a partial mitigation in the form of new endpoints which require authentication for media downloads. The unauthenticated endpoints will be frozen in a future release, closing the attack vector.

### Workarounds

Though extremely limited, server operators can use more strict rate limits based on IP address.

### References

* https://github.com/matrix-org/matrix-spec-proposals/pull/3916

### For more information

If you have any questions or comments about this advisory, please email us at [security at element.io](mailto:security@element.io).

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-gjgr-7834-rhxr
- https://nvd.nist.gov/vuln/detail/CVE-2024-37303
- https://github.com/matrix-org/matrix-spec-proposals/pull/3916
- https://github.com/element-hq/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2024-287.yaml
