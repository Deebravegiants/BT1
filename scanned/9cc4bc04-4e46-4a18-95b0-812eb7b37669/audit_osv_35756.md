# [H] Snowflake CLI SQL Injection Through Improper Neutralization of User-Controlled Input

## Summary
Severity: High
Advisory: CVE-2026-13744
CVSS: 8.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-13744
Type: osv

## Details
Improper neutralization of attacker-controlled content in Snowflake CLI versions prior to 3.19 allowed unintended SQL execution. By supplying crafted repository content, project configuration, manifest data, or specification input, an attacker could cause Snowflake CLI to execute unintended SQL in the context of the victim user's Snowflake session. Successful exploitation requires the victim to process attacker-controlled content through a vulnerable command path and is limited by the privileges assigned to that session. The fix is available in Snowflake CLI version 3.19. Users must manually upgrade.

## References
- https://community.snowflake.com/s/article/Snowflake-CLI-Vulnerability-Advisory
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13744.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13744
