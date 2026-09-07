# [H] Snowflake Connector .Net Command Injection

## Summary
Severity: High
Advisory: GHSA-223g-8w3x-98wr
CVE: CVE-2023-34230
CWE: CWE-77
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-06-09
Source: https://github.com/advisories/GHSA-223g-8w3x-98wr
Type: github-advisory

## Affected
- NuGet: `Snowflake.Data` — affected >=0 <2.0.18

## Details
### Issue
Snowflake was informed via our bug bounty program of a command injection vulnerability in the Snowflake .NET driver via SSO URL authentication.

### Impacted driver package: 
snowflake-connector-net

### Impacted version range: 
before [Version 2.0.18](https://community.snowflake.com/s/article/Dot-NET-Driver-Release-Notes)

### Attack Scenario
In order to exploit the potential for command injection, an attacker would need to be successful in (1) establishing a malicious resource and (2) redirecting users to utilize the resource. The attacker could set up a malicious, publicly accessible server which responds to the SSO URL with an attack payload. If the attacker then tricked a user into visiting the maliciously crafted connection URL, the user’s local machine would render the malicious payload, leading to a remote code execution. 

This attack scenario can be mitigated through URL whitelisting as well as common anti-phishing resources.  

### Solution
On December 2nd, 2022, Snowflake merged a patch that fixed a command injection vulnerability in the Snowflake .NET driver via SSO URL authentication. The vulnerability affected the Snowflake .NET driver before Version 2.0.18. We strongly recommend upgrading to the latest driver version as soon as possible via the following resources: [Snowflake .NET Driver](https://docs.snowflake.com/en/developer-guide/dotnet/dotnet-driver).

### Additional Information
If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/snowflakedb/snowflake-connector-net/security/advisories/GHSA-223g-8w3x-98wr
- https://nvd.nist.gov/vuln/detail/CVE-2023-34230
- https://github.com/snowflakedb/snowflake-connector-net
