# [M] Snowflake CLI SQL Injection Through Improper Neutralization of Parameters in Secret Creation and SPCS Service Log Commands

## Summary
Severity: Medium
Advisory: CVE-2026-13752
CVSS: 6.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-13752
Type: osv

## Details
Improper neutralization of parameters in Snowflake CLI versions prior to 3.19 allowed unintended SQL execution. An attacker could exploit this by supplying crafted values to vulnerable command paths, causing Snowflake CLI to execute unintended SQL in the context of the user’s Snowflake session. Successful exploitation required crafted values to reach vulnerable parameters, including through socially engineered input, malicious repository configuration, or compromised automation feeding external values into the CLI, and impact is limited by the privileges assigned to the active session. The fix is available in Snowflake CLI version 3.19, and users must manually upgrade.

## References
- https://community.snowflake.com/s/article/Snowflake-CLI-Vulnerability-Advisory
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13752.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13752
