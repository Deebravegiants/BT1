# [H] Regular expression denial of service in Delight Nashorn Sandbox

## Summary
Severity: High
Advisory: GHSA-38j3-6fm8-pfgc
CVE: CVE-2021-40660
CWE: CWE-1333
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-15
Source: https://github.com/advisories/GHSA-38j3-6fm8-pfgc
Type: github-advisory

## Affected
- Maven: `org.javadelight:delight-nashorn-sandbox` — affected >=0 <0.3.1

## Details
An issue was discovered in Delight Nashorn Sandbox. There is an ReDoS vulnerability that can be exploited to launching a denial of service (DoS) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40660
- https://github.com/javadelight/delight-nashorn-sandbox/issues/117
- https://github.com/javadelight/delight-nashorn-sandbox/issues/117#issuecomment-1564983722
- https://github.com/javadelight/delight-nashorn-sandbox/pull/139
- https://github.com/javadelight/delight-nashorn-sandbox/commit/b899b8ecad46090fdc042ac7683e1164114a69de
- https://github.com/javadelight/delight-nashorn-sandbox
- https://github.com/javadelight/delight-nashorn-sandbox/releases/tag/0.3.1
