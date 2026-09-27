# [C] Snowflake Connector for Python improperly verifies TLS hostnames

## Summary
Severity: Critical
Advisory: GHSA-5cc2-282f-jjq2
CVE: CVE-2026-15925
CWE: CWE-297
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-5cc2-282f-jjq2
Type: github-advisory

## Affected
- PyPI: `snowflake-connector-python` — affected >=0 <3.18.1
- PyPI: `snowflake-connector-python` — affected >=4.0.0 <4.7.1

## Details
Improper TLS hostname verification in Snowflake Connector for Python versions prior to 4.7.1 and 3.18.1 may have allowed a network-positioned attacker to bypass certificate hostname validation on HTTPS connections made by the connector. An attacker with on-path network access could exploit this by intercepting or redirecting network traffic and presenting a certificate signed by any trusted CA for any domain, causing the connector to accept connections without validating that the certificate matched the requested hostname. Successful exploitation requires an on-path traffic interception capability (e.g. ARP/DNS poisoning, rogue access point, BGP hijacking, or malicious proxy/exit node). This vulnerability may have exposed credentials, query data, and staged file contents to interception and tampering, and may have enabled the attacker to issue arbitrary SQL within the context of the victim's connector session. Impact is limited by the privileges of the affected Snowflake role. The fix is available in Snowflake Connector for Python versions 4.7.1 and 3.18.1. Users must manually upgrade.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-15925
- https://github.com/snowflakedb/snowflake-connector-python/commit/8969d6dc027092ee868965db022478b6c0fa40a1
- https://github.com/snowflakedb/snowflake-connector-python
- https://github.com/snowflakedb/snowflake-connector-python/releases/tag/v3.18.1
- https://github.com/snowflakedb/snowflake-connector-python/releases/tag/v4.7.1
