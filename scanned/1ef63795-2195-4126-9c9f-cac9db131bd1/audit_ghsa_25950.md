# [C] Code injection in Apache Dubbo

## Summary
Severity: Critical
Advisory: GHSA-qmfc-6www-fjqw
CVE: CVE-2021-30181
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-qmfc-6www-fjqw
Type: github-advisory

## Affected
- Maven: `com.alibaba:dubbo` — affected >=2.5.0 <2.6.9
- Maven: `org.apache.dubbo:dubbo` — affected >=2.5.0 <2.7.10

## Details
Apache Dubbo prior to 2.6.9 and 2.7.10 supports Script routing which will enable a customer to route the request to the right server. These rules are used by the customers when making a request in order to find the right endpoint. When parsing these rules, Dubbo customers use ScriptEngine and run the rule provided by the script which by default may enable executing arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30181
- https://lists.apache.org/thread.html/re22410dc704a09bc7032ddf15140cf5e7df3e8ece390fc9032ff5587%40%3Cdev.dubbo.apache.org%3E
