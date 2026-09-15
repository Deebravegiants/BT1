# [H] Remote Code Execution (RCE) via Server Side Template Injection (SSTI) in Airbyte

## Summary
Severity: High
Advisory: CVE-2024-38363
Aliases: GHSA-4j3c-fgvx-xgqq
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/CVE-2024-38363
Type: osv

## Details
Airbyte is a data integration platform for ELT pipelines. Airbyte connection builder docker image is vulnerable to RCE via SSTI which allows an authenticated remote attacker to execute arbitrary code on the server as the web server user. The connection builder is used to create and test new connectors. Sensitive information, such as credentials, could be exposed if a user tested a new connector on a compromised instance. The connection builder does not have access to any data processes. This vulnerability is fixed in 0.62.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38363.json
- https://github.com/airbytehq/airbyte/security/advisories/GHSA-4j3c-fgvx-xgqq
- https://nvd.nist.gov/vuln/detail/CVE-2024-38363
