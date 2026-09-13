# [M] Snowflake CLI Server-Side Request Forgery via Arbitrary URL Fetch in !source/!load

## Summary
Severity: Medium
Advisory: CVE-2026-13751
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-13751
Type: osv

## Details
Improper handling of untrusted remote references in Snowflake CLI versions prior to 3.19 allowed server-side request forgery. The SQL statement reader's !source/!load directives could reference remote URLs that were retrieved at runtime without sufficient restriction on the request destination. By supplying crafted SQL content processed through a vulnerable command path, an attacker could cause the victim's environment to issue unintended outbound requests to internal or otherwise non-public network locations, and could cause remote SQL content to be retrieved and executed in the context of the victim user's session. Successful exploitation requires the victim to process attacker-controlled content through a vulnerable command path and is limited by the privileges available to that session and environment. The fix is available in Snowflake CLI version 3.19, which adds an option to disable remote URL retrieval.

## References
- https://community.snowflake.com/s/article/Snowflake-CLI-Vulnerability-Advisory
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13751.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13751
