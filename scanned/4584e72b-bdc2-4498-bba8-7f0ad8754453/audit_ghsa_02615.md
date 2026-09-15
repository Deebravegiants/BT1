# [C] Remote Code Execution in Apache Dubbo

## Summary
Severity: Critical
Advisory: GHSA-qvm7-23cj-437v
CVE: CVE-2021-36161
CWE: CWE-134
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-10
Source: https://github.com/advisories/GHSA-qvm7-23cj-437v
Type: github-advisory

## Affected
- Maven: `org.apache.dubbo:dubbo` — affected >=0 <2.7.13

## Details
Some component in Dubbo will try to print the formated string of the input arguments, which will possibly cause RCE for a maliciously customized bean with special toString method. In the latest version, we fix the toString call in timeout, cache and some other places. Fixed in Apache Dubbo 2.7.13

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-36161
- https://github.com/apache/dubbo
- https://lists.apache.org/thread.html/r40212261fd5d638074b65f22ac73eebe93ace310c79d4cfcca4863da%40%3Cdev.dubbo.apache.org%3E
