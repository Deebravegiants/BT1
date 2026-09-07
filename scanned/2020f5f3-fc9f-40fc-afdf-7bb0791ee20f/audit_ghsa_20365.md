# [H] Unsafe deserialization in com.alibaba:fastjson

## Summary
Severity: High
Advisory: GHSA-pv7h-hx5h-mgfj
CVE: CVE-2022-25845
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-11
Source: https://github.com/advisories/GHSA-pv7h-hx5h-mgfj
Type: github-advisory

## Affected
- Maven: `com.alibaba:fastjson` — affected >=1.2.25 <1.2.83

## Details
The package com.alibaba:fastjson before 1.2.83 is vulnerable to Deserialization of Untrusted Data by bypassing the default autoType shutdown restrictions, which is possible under certain conditions. Exploiting this vulnerability allows attacking remote servers. Workaround: If upgrading is not possible, you can enable [safeMode](https://github.com/alibaba/fastjson/wiki/fastjson_safemode).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25845
- https://github.com/alibaba/fastjson/commit/35db4adad70c32089542f23c272def1ad920a60d
- https://github.com/alibaba/fastjson/commit/8f3410f81cbd437f7c459f8868445d50ad301f15
- https://github.com/alibaba/fastjson
- https://github.com/alibaba/fastjson/releases/tag/1.2.83
- https://github.com/alibaba/fastjson/wiki/security_update_20220523
- https://snyk.io/vuln/SNYK-JAVA-COMALIBABA-2859222
- https://www.ddosi.org/fastjson-poc
- https://www.oracle.com/security-alerts/cpujul2022.html
