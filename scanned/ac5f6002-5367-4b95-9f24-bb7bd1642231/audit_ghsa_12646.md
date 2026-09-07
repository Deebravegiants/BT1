# [H] Snowflake Python Connector vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-5w5m-pfw9-c8fp
CVE: CVE-2023-34233
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-5w5m-pfw9-c8fp
Type: github-advisory

## Affected
- PyPI: `snowflake-connector-python` — affected >=0 <3.0.2

## Details
### Issue
Snowflake was informed via our bug bounty program of a command injection vulnerability in the Snowflake Python connector via SSO browser URL authentication. 

### Impacted driver package: 
snowflake-connector-python

### Impacted version range: 
before [Version 3.0.2](https://community.snowflake.com/s/article/Snowflake-Connector-for-Python-Release-Notes)

### Attack Scenario
In order to exploit the potential for command injection, an attacker would need to be successful in (1) establishing a malicious resource and (2) redirecting users to utilize the resource. The attacker could set up a malicious, publicly accessible server which responds to the SSO URL with an attack payload. If the attacker then tricked a user into visiting the maliciously crafted connection URL, the user’s local machine would render the malicious payload, leading to a remote code execution. 

This attack scenario can be mitigated through URL whitelisting as well as common anti-phishing resources.   

### Solution
On March 23rd, 2023, Snowflake merged a patch that fixed a command injection vulnerability in the Snowflake Python connector via SSO browser URL authentication. The vulnerability affected the Snowflake Python connector before Version 3.0.2. We strongly recommend users upgrade to Version 3.0.2 as soon as possible via the following resources: [Snowflake Python Connector](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector)

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-connector-python/security/advisories/GHSA-5w5m-pfw9-c8fp
- https://nvd.nist.gov/vuln/detail/CVE-2023-34233
- https://github.com/snowflakedb/snowflake-connector-python/pull/1480
- https://github.com/snowflakedb/snowflake-connector-python/commit/1cdbd3b1403c5ef520d7f4d9614fe35165e101ac
- https://github.com/pypa/advisory-database/tree/main/vulns/snowflake-connector-python/PYSEC-2023-88.yaml
- https://github.com/snowflakedb/snowflake-connector-python
