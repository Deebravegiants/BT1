# [M] Synapse vulnerable to leak of remote user device information

## Summary
Severity: Medium
Advisory: GHSA-mp92-3jfm-3575
CVE: CVE-2023-43796
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-31
Source: https://github.com/advisories/GHSA-mp92-3jfm-3575
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.95.1

## Details
### Impact
Cached device information of remote users can be queried from Synapse. This can be used to enumerate the remote users known to a homeserver.

### Patches
System administrators are encouraged to upgrade to Synapse 1.95.1 as soon as possible.

### Workarounds
The `federation_domain_whitelist` can be used to limit federation traffic with a homeserver.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-mp92-3jfm-3575
- https://nvd.nist.gov/vuln/detail/CVE-2023-43796
- https://github.com/matrix-org/synapse/commit/daec55e1fe120c564240c5386e77941372bf458f
- https://github.com/matrix-org/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2023-230.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2IDEEZMFJBDLTFHQUTZRJJNCOZGQ2ZVS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VH3RNC5ZPQZ4OKPSL4E6BBJSZOQLGDEY
- https://security.gentoo.org/glsa/202401-12
