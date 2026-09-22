# [M] OpenC3 Cross-site Scripting in Login functionality (`GHSL-2024-128`)

## Summary
Severity: Medium
Advisory: GHSA-vfj8-5pj7-2f9g
CVE: CVE-2024-43795
CWE: CWE-79
Ecosystem: PyPI, RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-vfj8-5pj7-2f9g
Type: github-advisory

## Affected
- RubyGems: `openc3` — affected >=0 <5.19.0
- npm: `@openc3/tool-common` — affected >=0 <5.19.0
- PyPI: `openc3` — affected >=0 <5.19.0

## Details
### Summary
The login functionality contains a reflected cross-site scripting (XSS) vulnerability.

Note: This CVE only affects Open Source Edition, and not OpenC3 COSMOS Enterprise Edition

### Impact
This issue may lead up to Remote Code Execution (RCE).

## References
- https://github.com/OpenC3/cosmos/security/advisories/GHSA-vfj8-5pj7-2f9g
- https://nvd.nist.gov/vuln/detail/CVE-2024-43795
- https://github.com/OpenC3/cosmos/commit/762d7e0e93bdc2f340b1e42acccedc78994a576e
- https://github.com/OpenC3/cosmos
- https://github.com/pypa/advisory-database/tree/main/vulns/openc3/PYSEC-2024-100.yaml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openc3/CVE-2024-43795.yml
- https://securitylab.github.com/advisories/GHSL-2024-127_GHSL-2024-129_OpenC3_COSMOS
