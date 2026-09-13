# [H] vantage6 refresh tokens do not expire

## Summary
Severity: High
Advisory: GHSA-4w59-c3gc-rrhp
CVE: CVE-2023-23929
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-28
Source: https://github.com/advisories/GHSA-4w59-c3gc-rrhp
Type: github-advisory

## Affected
- PyPI: `vantage6` — affected >=0 <3.8.0

## Details
From issue: 

Problem description
Currently, the refresh token is valid indefinitely. This is bad security practice.

Desired solution
The refresh token should get a validity of 24-48 hours.

Additional context

When implementing this, also check that the refresh token returns a new refresh token
When implementing this, also adapt the UI so that it logs out if refresh token is no longer valid.
When implementing this, ensure that nodes refresh their token periodically so that they do not have to be restarted manually.


### Impact
### Patches
None available 

### Workarounds
None available

## References
- https://github.com/vantage6/vantage6/security/advisories/GHSA-4w59-c3gc-rrhp
- https://nvd.nist.gov/vuln/detail/CVE-2023-23929
- https://github.com/vantage6/vantage6/commit/48ebfca42359e9a6743e9598684585e2522cdce8
- https://github.com/pypa/advisory-database/tree/main/vulns/vantage6/PYSEC-2023-54.yaml
- https://github.com/vantage6/vantage6
