# [M] Sydent DoS (via resource exhaustion) due to improper input validation

## Summary
Severity: Medium
Advisory: GHSA-pw4v-gr34-2553
CVE: CVE-2021-29433
CWE: CWE-20, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-04-16
Source: https://github.com/advisories/GHSA-pw4v-gr34-2553
Type: github-advisory

## Affected
- PyPI: `matrix-sydent` — affected >=0 <2.3.0

## Details
### Impact

Missing input validation of some parameters on the endpoints used to confirm third-party identifiers could cause excessive use of disk space and memory leading to resource exhaustion.

### Patches

Fixed by 3175fd3.

### For more information

If you have any questions or comments about this advisory, email us at security@matrix.org.

## References
- https://github.com/matrix-org/sydent/security/advisories/GHSA-pw4v-gr34-2553
- https://nvd.nist.gov/vuln/detail/CVE-2021-29433
- https://github.com/matrix-org/sydent/commit/3175fd358ebc2c310eab7a3dbf296ce2bd54c1da
- https://github.com/matrix-org/sydent
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-sydent/PYSEC-2021-24.yaml
- https://pypi.org/project/matrix-sydent
