# [H] Snowflake Golang Driver vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-fwv2-65wh-2w8c
CVE: CVE-2023-34231
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-fwv2-65wh-2w8c
Type: github-advisory

## Affected
- Go: `github.com/snowflakedb/gosnowflake` — affected >=0 <1.6.19

## Details
### Issue
Snowflake was informed via our bug bounty program of a command injection vulnerability in the Snowflake Golang driver via SSO browser URL authentication.

### Impacted driver package: 
gosnowflake

### Impacted version range: 
before [Version 1.6.19](https://community.snowflake.com/s/article/Go-Snowflake-Driver-Release-Notes)

### Attack Scenario
In order to exploit the potential for command injection, an attacker would need to be successful in (1) establishing a malicious resource and (2) redirecting users to utilize the resource. The attacker could set up a malicious, publicly accessible server which responds to the SSO URL with an attack payload. If the attacker then tricked a user into visiting the maliciously crafted connection URL, the user’s local machine would render the malicious payload, leading to a remote code execution. 

This attack scenario can be mitigated through URL whitelisting as well as common anti-phishing resources.  

### Solution
On March 21, 2023, Snowflake merged a patch that fixed a command injection vulnerability in the Snowflake Golang driver via SSO browser URL authentication. The vulnerability affected the Snowflake Golang driver before Version 1.6.19. We strongly recommend users upgrade to Version 1.6.19 as soon as possible via the following resources: [Go Snowflake Driver](https://docs.snowflake.com/en/developer-guide/golang/go-driver)

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/gosnowflake/security/advisories/GHSA-fwv2-65wh-2w8c
- https://nvd.nist.gov/vuln/detail/CVE-2023-34231
- https://github.com/snowflakedb/gosnowflake/pull/757
- https://github.com/snowflakedb/gosnowflake/commit/e11a2a555f1b9f7adc1f01fb7b5e7f38fbbb2a1c
- https://github.com/snowflakedb/gosnowflake
