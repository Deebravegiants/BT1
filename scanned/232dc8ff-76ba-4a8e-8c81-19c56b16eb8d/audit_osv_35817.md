# [H] Multiple Security Vulnerabilities in Terraform Provider for Snowflake Could Allow Privilege Escalation and Unauthorized Snowflake Account Takeover

## Summary
Severity: High
Advisory: CVE-2026-15067
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-15067
Type: osv

## Details
Snowflake Terraform Provider versions prior to 2.18.0 contain several security vulnerabilities, including SQL injection via an unsanitized data source input could result in arbitrary SQL execution under the provider's privileged Snowflake session, potentially enabling sensitive data exfiltration and minting of long-lived access credentials. Exploitation requires the ability for an attacker to  influence a workspace variable in a pipeline where this data source was enabled. Improper neutralization of identifier content in user resource inputs could allow DDL injection into user management statements, potentially causing accounts to be created with attacker-controlled credentials and without the  security controls configured by the operator. The fix is available in Snowflake Terraform Provider version 2.18.0. Users must manually upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15067.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15067
- https://github.com/snowflakedb/terraform-provider-snowflake/releases
