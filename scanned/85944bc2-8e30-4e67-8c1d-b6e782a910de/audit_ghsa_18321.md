# [C] H2O affected by a deserialization vulnerability

## Summary
Severity: Critical
Advisory: GHSA-5w3j-gwgh-4rfv
CVE: CVE-2025-6544
CWE: CWE-502
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-22
Source: https://github.com/advisories/GHSA-5w3j-gwgh-4rfv
Type: github-advisory

## Affected
- Maven: `ai.h2o:h2o-core` — affected >=0
- PyPI: `h2o` — affected >=0

## Details
A deserialization vulnerability exists in h2oai/h2o-3 versions <= 3.46.0.7, allowing attackers to read arbitrary system files and execute arbitrary code. The vulnerability arises from improper handling of JDBC connection parameters, which can be exploited by bypassing regular expression checks and using double URL encoding. This issue impacts all users of the affected versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-6544
- https://github.com/h2oai/h2o-3/commit/0298ee348f5c73673b7b542158081e79605f5f25
- https://github.com/h2oai/h2o-3
- https://huntr.com/bounties/53f35a0f-d644-4f82-93aa-89fe7e0aed40
