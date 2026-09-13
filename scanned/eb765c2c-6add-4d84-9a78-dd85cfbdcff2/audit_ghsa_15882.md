# [M] OpenC3 stores passwords in clear text (`GHSL-2024-129`)

## Summary
Severity: Medium
Advisory: GHSA-4xqv-47rm-37mm
CVE: CVE-2024-47529
CWE: CWE-312, CWE-522
Ecosystem: PyPI, RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-4xqv-47rm-37mm
Type: github-advisory

## Affected
- RubyGems: `openc3` — affected >=0 <5.19.0
- npm: `@openc3/tool-common` — affected >=0 <5.19.0
- PyPI: `openc3` — affected >=0 <5.19.0

## Details
### Summary
OpenC3 COSMOS stores the password of a user unencrypted in the LocalStorage of a web browser. This makes the user password susceptible to exfiltration via Cross-site scripting (see GHSL-2024-128).

Note: This CVE only affects Open Source edition, and not OpenC3 COSMOS Enterprise Edition

### Impact
This issue may lead to Information Disclosure.

## References
- https://github.com/OpenC3/cosmos/security/advisories/GHSA-4xqv-47rm-37mm
- https://nvd.nist.gov/vuln/detail/CVE-2024-47529
- https://github.com/OpenC3/cosmos/commit/b5ab34fe7fa54c0c8171c4aa3caf4e03d6f63bd7
- https://github.com/OpenC3/cosmos
- https://github.com/pypa/advisory-database/tree/main/vulns/openc3/PYSEC-2024-121.yaml
- https://securitylab.github.com/advisories/GHSL-2024-127_GHSL-2024-129_OpenC3_COSMOS
