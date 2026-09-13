# [H] Snowflake CLI Arbitrary Code Execution via Snowpark Annotation Processor Template Injection

## Summary
Severity: High
Advisory: CVE-2026-13749
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-13749
Type: osv

## Details
Improper neutralization in the Snowpark annotation processor callback template in Snowflake CLI versions prior to 3.19 allowed arbitrary code execution during application bundling or deployment. An attacker could exploit this by supplying crafted project content that is interpolated into generated Python code, causing Snowflake CLI to execute attacker-controlled code in the local context of the user running the CLI. Successful exploitation requires the victim to run the relevant bundling or deployment workflow against attacker-controlled project content, and any resulting code runs with the privileges of that local execution context. The fix is available in Snowflake CLI version 3.19, and users must manually upgrade.

## References
- https://community.snowflake.com/s/article/Snowflake-CLI-Vulnerability-Advisory
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13749.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13749
