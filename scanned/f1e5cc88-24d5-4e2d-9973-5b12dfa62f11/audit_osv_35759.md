# [M] Snowflake CLI Sensitive Credential Exposure Through Debug Logging

## Summary
Severity: Medium
Advisory: CVE-2026-13750
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-13750
Type: osv

## Details
Insertion of sensitive information into log files in Snowflake CLI versions prior to 3.19 allowed plaintext credentials to be written to persistent local debug logs. An attacker could exploit this by obtaining read access to the affected user's local log files, causing credentials such as passwords, tokens, or private key material to be exposed without additional application-level safeguards. Successful exploitation requires credentials to be present in the affected connection context and the resulting logs to be accessible from the local environment. The fix is available in Snowflake CLI version 3.19, and users must manually upgrade.

## References
- https://community.snowflake.com/s/article/Snowflake-CLI-Vulnerability-Advisory
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13750.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13750
