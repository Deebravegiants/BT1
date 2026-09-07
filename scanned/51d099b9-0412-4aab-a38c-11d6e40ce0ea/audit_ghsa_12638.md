# [H] Snowflake NodeJS Driver vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-h53w-7qw7-vh5c
CVE: CVE-2023-34232
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-h53w-7qw7-vh5c
Type: github-advisory

## Affected
- npm: `snowflake-sdk` — affected >=0 <1.6.21

## Details
### Issue
Snowflake was informed via our bug bounty program of a command injection vulnerability in the Snowflake NodeJS driver via SSO browser URL authentication.

### Impacted driver package: 
snowflake-connector-nodejs

### Impacted version range: 
before [Version 1.6.21](https://community.snowflake.com/s/article/Node-js-Driver-Release-Notes) 

### Attack Scenario
In order to exploit the potential for command injection, an attacker would need to be successful in (1) establishing a malicious resource and (2) redirecting users to utilize the resource. The attacker could set up a malicious, publicly accessible server which responds to the SSO URL with an attack payload. If the attacker then tricked a user into visiting the maliciously crafted connection URL, the user’s local machine would render the malicious payload, leading to a remote code execution. 

This attack scenario can be mitigated through URL whitelisting as well as common anti-phishing resources.  

### Solution
On April 18, 2023, Snowflake merged a patch that fixed a command injection vulnerability in the Snowflake NodeJS driver via SSO browser URL authentication. The vulnerability affected the Snowflake NodeJS driver before Version 1.6.21. We strongly recommend users upgrade to Version 1.6.21 as soon as possible via the following resources: [Snowflake NodeJS Driver](https://docs.snowflake.com/en/developer-guide/node-js/nodejs-driver)

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-connector-nodejs/security/advisories/GHSA-h53w-7qw7-vh5c
- https://nvd.nist.gov/vuln/detail/CVE-2023-34232
- https://github.com/snowflakedb/snowflake-connector-nodejs/pull/465
- https://github.com/snowflakedb/snowflake-connector-nodejs/commit/0c9622ae12cd7d627df404b73a783b4a5f60728a
- https://community.snowflake.com/s/article/Node-js-Driver-Release-Notes
- https://github.com/snowflakedb/snowflake-connector-nodejs
