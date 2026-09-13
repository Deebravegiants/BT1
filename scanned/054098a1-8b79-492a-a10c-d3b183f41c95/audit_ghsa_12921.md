# [C] Dromara Hutool Deserialization of Untrusted Data vulnerability

## Summary
Severity: Critical
Advisory: GHSA-77h8-5j3h-jcjf
CVE: CVE-2023-24162
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-31
Source: https://github.com/advisories/GHSA-77h8-5j3h-jcjf
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-all` — affected >=0

## Details
Deserialization vulnerability in Dromara Hutool v5.8.11 allows attacker to execute arbitrary code via the XmlUtil.readObjectFromXml parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24162
- https://github.com/dromara/hutool/issues/2855
- https://gitee.com/dromara/hutool
- https://gitee.com/dromara/hutool/issues/I6AEX2
