# [C] Improper Input Validation in alilibaba:fastjson

## Summary
Severity: Critical
Advisory: GHSA-xjrr-xv9m-4pw5
CVE: CVE-2017-18349
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-24
Source: https://github.com/advisories/GHSA-xjrr-xv9m-4pw5
Type: github-advisory

## Affected
- Maven: `com.alibaba:fastjson` — affected >=0 <1.2.31
- Maven: `ro.pippo:pippo-fastjson` — affected >=0 <1.12.0

## Details
parseObject in Fastjson before 1.2.25, as used in FastjsonEngine in Pippo 1.11.0 and other products, allows remote attackers to execute arbitrary code via a crafted JSON request, as demonstrated by a crafted rmi:// URI in the dataSourceName field of HTTP POST data to the Pippo /json URI, which is mishandled in AjaxApplication.java.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18349
- https://github.com/pippo-java/pippo/issues/466
- https://github.com/pippo-java/pippo/commit/8443377d3c5b35acca190a66894b4f95e4051be2
- https://fortiguard.com/encyclopedia/ips/44059
- https://github.com/advisories/GHSA-xjrr-xv9m-4pw5
- https://github.com/alibaba/fastjson
- https://github.com/alibaba/fastjson/wiki/security_update_20170315
