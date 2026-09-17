# [H] Improper Verification of Cryptographic Signature in matrix-synapse

## Summary
Severity: High
Advisory: GHSA-cppw-2mf8-qpm5
CVE: CVE-2019-18835
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cppw-2mf8-qpm5
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.5.0

## Details
Matrix Synapse before 1.5.0 mishandles signature checking on some federation APIs. Events sent over `/send_join`, `/send_leave`, and `/invite` may not be correctly signed, or may not come from the expected servers.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18835
- https://github.com/matrix-org/synapse/pull/6262
- https://github.com/matrix-org/synapse/commit/172f264ed38e8bef857552f93114b4ee113a880b
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v1.5.0
- https://github.com/pypa/advisory-database/tree/main/vulns/matrix-synapse/PYSEC-2019-186.yaml
