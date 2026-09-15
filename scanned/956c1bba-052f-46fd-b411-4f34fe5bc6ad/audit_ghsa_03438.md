# [M] Denial of service (via resource exhaustion) due to improper input validation on groups/communities endpoints

## Summary
Severity: Medium
Advisory: GHSA-jrh7-mhhx-6h88
CVE: CVE-2021-21393
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-jrh7-mhhx-6h88
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.28.0

## Details
### Impact
Missing input validation of some parameters on the groups (also known as communities) endpoints could cause excessive use of disk space and memory leading to resource exhaustion. Additionally clients may have issues rendering large fields.

### Patches
This issue is fixed by #9321 and #9393.

### Workarounds
The groups feature can be disabled (by setting `enable_group_creation` to `False`) to mitigate this issue. Note that it is disabled by default.

### Other information
Note that the groups feature is not part of the [Matrix specification](https://matrix.org/docs/spec/) and the chosen maximum lengths are arbitrary. Not all clients might abide by them.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-jrh7-mhhx-6h88
- https://nvd.nist.gov/vuln/detail/CVE-2021-21393
- https://github.com/matrix-org/synapse/pull/9321
- https://github.com/matrix-org/synapse/pull/9393
- https://github.com/matrix-org/synapse/commit/3f58fc848d0002de4605bed91603a1f9f245d128
- https://github.com/matrix-org/synapse/commit/d2f0ec12d5c8f113095408888e87e191ac546499
- https://github.com/matrix-org/synapse
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2021-26.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TNNAJOZNMVMXM6AS7RFFKB4QLUJ4IFEY
- https://pypi.org/project/matrix-synapse
