# [H] A deserialization flaw in the Chainsaw component of Log4j 1 can lead to malicious code execution.

## Summary
Severity: High
Advisory: CVE-2022-23307
Aliases: GHSA-f7vh-qwp3-x37m
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-18
Source: https://osv.dev/vulnerability/CVE-2022-23307
Type: osv

## Details
CVE-2020-9493 identified a deserialization issue that was present in Apache Chainsaw. Prior to Chainsaw V2.0 Chainsaw was a component of Apache Log4j 1.2.x where the same issue exists.

## References
- https://lists.apache.org/thread/rg4yyc89vs3dw6kpy3r92xop9loywyhh
- https://logging.apache.org/log4j/1.2/index.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23307.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-23307
