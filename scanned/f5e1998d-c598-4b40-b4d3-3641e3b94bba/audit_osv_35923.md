# [H] Multiple Security Vulnerabilities in Snowflake libsnowflakeclient

## Summary
Severity: High
Advisory: CVE-2026-16870
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-16870
Type: osv

## Details
Multiple security vulnerabilities in Snowflake libsnowflakeclient versions prior to 2.9.2 could allow remote code execution and credential exfiltration. A stack-based buffer overflow in the file download path could allow remote code execution on a victim host. An attacker could exploit this by uploading a file with a crafted encryption metadata field to a shared internal stage that a victim process later downloads, and impact would be limited to deployments where principals with different privilege levels share the same internal stage. A related out-of-bounds write in the same download path could allow memory corruption with attacker-controlled write primitives. An attacker may exploit this through a crafted initialization vector metadata field on a shared stage, and impact would be limited by the same stage-write precondition. Improper validation of connection parameters could allow an attacker-controlled input to redirect outbound authentication requests — including credentials and tokens — to an attacker-controlled endpoint. Impact is limited to embedding deployments where a lower-privileged principal can influence connection configuration while higher-privileged service credentials are in use. The fix is available in Snowflake libsnowflakeclient version 2.9.2. The Snowflake PHP PDO Driver and Snowflake ODBC Driver embed the affected library; fixes are available in versions 4.1.0 and 3.19.0 respectively. Users must manually upgrade.

## References
- https://github.com/snowflakedb/libsnowflakeclient/releases/tag/v2.9.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16870.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-16870
