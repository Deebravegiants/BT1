# [H] Databricks JDBC Driver Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-jxw2-jvxf-5vrp
CVE: CVE-2024-49194
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-12-17
Source: https://github.com/advisories/GHSA-jxw2-jvxf-5vrp
Type: github-advisory

## Affected
- Maven: `com.databricks:databricks-jdbc` — affected >=2.0 <2.6.40

## Details
Databricks JDBC Driver 2.x before 2.6.40 could potentially allow remote code execution (RCE) by triggering a JNDI injection via a JDBC URL parameter. The vulnerability is rooted in the improper handling of the krbJAASFile parameter. An attacker could potentially exploit this vulnerability to achieve Remote Code Execution in the context of the driver by tricking a victim into using a crafted connection URL that uses the property krbJAASFile.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-49194
- https://github.com/databricks/databricks-jdbc
- http://kb.databricks.com/en_US/data-sources/security-bulletin-databricks-jdbc-driver-vulnerability-advisory-cve-2024-49194
