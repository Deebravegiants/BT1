# [M] Snowflake CLI Arbitrary Local File Read and Exfiltration Through Improper File Path Restriction

## Summary
Severity: Medium
Advisory: CVE-2026-13748
CVSS: 6.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-13748
Type: osv

## Details
Improper restriction of file path resolution in Snowflake CLI versions prior to 3.19 allowed arbitrary local file content to be read and transmitted to Snowflake services. An attacker could exploit this by supplying crafted repository or project content that referenced files outside the intended project boundary, causing Snowflake CLI to read local files and upload or embed their contents during deployment or SQL template processing. Successful exploitation required the victim to process attacker-controlled project content, and retrieval of exfiltrated data depended on access to the victim's Snowflake account artifacts such as query history or uploaded stage content. The fix is available in Snowflake CLI version 3.19, and users must manually upgrade.

## References
- https://community.snowflake.com/s/article/Snowflake-CLI-Vulnerability-Advisory
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13748.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13748
