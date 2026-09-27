# [H] Matrix Synapse Security Filtering Flaw

## Summary
Severity: High
Advisory: GHSA-v8wm-g9f2-xjv4
CVE: CVE-2018-12291
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-v8wm-g9f2-xjv4
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <0.31.1

## Details
The `on_get_missing_events` function in handlers/federation.py in Matrix Synapse before 0.31.1 has a security bug in the get_missing_events federation API where event visibility rules were not applied correctly.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12291
- https://github.com/matrix-org/synapse/pull/3371
- https://github.com/matrix-org/synapse/commit/0834b49c6a9b6c597a154d4b2dfcf8fff90699ec
- https://github.com/matrix-org/synapse
- https://github.com/matrix-org/synapse/releases/tag/v0.31.1
