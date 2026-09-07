# [M] Denial of service (via resource exhaustion) due to improper input validation in third-party identifier endpoint

## Summary
Severity: Medium
Advisory: GHSA-7h5v-85w9-pq6c
CWE: CWE-400
Ecosystem: PyPI
Published: 2021-05-19
Source: https://github.com/advisories/GHSA-7h5v-85w9-pq6c
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.33.0

## Details
### Impact
Missing input validation of some parameters on the endpoints used to confirm third-party identifiers could cause excessive use of disk space and memory leading to resource exhaustion.

### Patches
The issue is fixed by https://github.com/matrix-org/synapse/pull/9855.

### Workarounds
There are no known workarounds.

### References
n/a

### For more information
If you have any questions or comments about this advisory, email us at security@matrix.org.

## References
- https://github.com/matrix-org/synapse/security/advisories/GHSA-7h5v-85w9-pq6c
- https://github.com/matrix-org/synapse/pull/9855
