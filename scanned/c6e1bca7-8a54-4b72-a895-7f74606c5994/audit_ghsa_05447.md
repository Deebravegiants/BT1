# [C] FASTJSON Includes Functionality from Untrusted Control Sphere 

## Summary
Severity: Critical
Advisory: GHSA-jm7w-5684-pvh8
CVE: CVE-2025-70974
CWE: CWE-829
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-09
Source: https://github.com/advisories/GHSA-jm7w-5684-pvh8
Type: github-advisory

## Affected
- Maven: `com.alibaba:fastjson` — affected >=0 <1.2.48

## Details
Fastjson before 1.2.48 mishandles autoType because, when an `@type` key is in a JSON document, and the value of that key is the name of a Java class, there may be calls to certain public methods of that class. Depending on the behavior of those methods, there may be JNDI injection with an attacker-supplied payload located elsewhere in that JSON document. This was exploited in the wild in 2023 through 2025. NOTE: this issue exists because of an incomplete fix for CVE-2017-18349. Also, a later bypass is covered by CVE-2022-25845.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-70974
- https://github.com/alibaba/fastjson
- https://github.com/alibaba/fastjson/compare/1.2.47...1.2.48
- https://github.com/vulhub/vulhub/tree/master/fastjson/1.2.47-rce
- https://web.archive.org/web/20220121055754/https://cert.360.cn/warning/detail?id=7240aeab581c6dc2c9c5350756079955
- https://www.cloudsek.com/blog/androxgh0st-continues-exploitation-operators-compromise-a-us-university-for-hosting-c2-logger
- https://www.cnvd.org.cn/flaw/show/CNVD-2019-22238
- https://www.freebuf.com/vuls/208339.html
- https://www.seebug.org/vuldb/ssvid-98020
