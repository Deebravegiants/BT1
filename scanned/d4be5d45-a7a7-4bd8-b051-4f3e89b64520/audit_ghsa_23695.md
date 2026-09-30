# [H] matrix-sydent and matrix-synapse Use Cryptographically Weak PRNG

## Summary
Severity: High
Advisory: GHSA-gwf7-vfjf-wf6x
CVE: CVE-2019-11842
CWE: CWE-338
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gwf7-vfjf-wf6x
Type: github-advisory

## Affected
- PyPI: `matrix-sydent` — affected >=0 <1.0.3
- PyPI: `matrix-synapse` — affected >=0 <0.99.3.1

## Details
An issue was discovered in Matrix Sydent before 1.0.3 and Synapse before 0.99.3.1. Random number generation is mishandled, which makes it easier for attackers to predict a Sydent authentication token or a Synapse random ID.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-11842
- https://github.com/advisories/GHSA-gwf7-vfjf-wf6x
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2019-185.yaml
- https://matrix.org/blog/2019/05/03/security-updates-sydent-1-0-3-synapse-0-99-3-1-and-riot-android-0-9-0-0-8-99-0-8-28-a
