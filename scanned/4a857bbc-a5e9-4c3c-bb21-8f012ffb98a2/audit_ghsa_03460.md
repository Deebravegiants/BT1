# [H] Open redirect via transitional IPv6 addresses on dual-stack networks

## Summary
Severity: High
Advisory: GHSA-5wrh-4jwv-5w78
CVE: CVE-2021-21392
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-5wrh-4jwv-5w78
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.28.0rc1

## Details
### Impact
Requests to user provided domains were not restricted to external IP addresses when transitional IPv6 addresses were used. Outbound requests to federation, identity servers, when calculating the key validity for third-party invite events, sending push notifications, and generating URL previews are affected. This could cause Synapse to make requests to internal infrastructure on dual-stack networks.

### Patches
This issue is fixed by #9240.

### Workarounds
Outbound requests to the following address ranges can be blocked by a firewall, if unused for internal communication between systems:

* `::ffff/80`
* `::0000/80` (note that this IP range is considered deprecated by the IETF)
* `2002::/16` (note that this IP range is considered deprecated by the IETF)

### References
* [RFC3056](https://tools.ietf.org/html/rfc3056)
* [RFC4291](https://tools.ietf.org/html/rfc4291)

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-5wrh-4jwv-5w78
- https://nvd.nist.gov/vuln/detail/CVE-2021-21392
- https://github.com/matrix-org/synapse/pull/9240
- https://github.com/matrix-org/synapse/commit/4ca054a4eaa714d0befb4fc30b19a1131e52c9cc
- https://github.com/matrix-org/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2021-25.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TNNAJOZNMVMXM6AS7RFFKB4QLUJ4IFEY
- https://pypi.org/project/matrix-synapse
