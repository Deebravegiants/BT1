# [H] json stack overflow vulnerability

## Summary
Severity: High
Advisory: GHSA-3vqj-43w4-2q58
CVE: CVE-2022-45688
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-3vqj-43w4-2q58
Type: github-advisory

## Affected
- Maven: `cn.hutool:hutool-json` — affected >=0 <5.8.25
- Maven: `org.json:json` — affected >=0 <20230227

## Details
A stack overflow in the XML.toJSONObject component of hutool-json v5.8.10 and org.json:json before version 20230227 allows attackers to cause a Denial of Service (DoS) via crafted JSON or XML data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45688
- https://github.com/dromara/hutool/issues/2748
- https://github.com/stleary/JSON-java/issues/708
- https://github.com/dromara/hutool/commit/6a2b585de0a380e8c12016dbaa1620b69be11b8c
- https://github.com/stleary/JSON-java/commit/a6e412bded7a0ad605adfeca029318f184c32102
- https://github.com/dromara/hutool/releases/tag/5.8.25
