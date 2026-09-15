# [M] weixin4j has Improperly Controlled Sequential Memory Allocation 

## Summary
Severity: Medium
Advisory: GHSA-444m-px7r-qpvv
CVE: CVE-2026-24819
CWE: CWE-1325
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N/AU:Y/R:A/V:D/RE:M/U:Amber (CVSS_V4)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-444m-px7r-qpvv
Type: github-advisory

## Affected
- Maven: `com.foxinmy:weixin4j-base` — affected >=0

## Details
Improperly Controlled Sequential Memory Allocation vulnerability in foxinmy weixin4j (weixin4j-base/src/main/java/com/foxinmy/weixin4j/util modules). This vulnerability is associated with program files CharArrayBuffer.Java, ClassUtil.Java.

This issue affects all versions of weixin4j. A path is available:  [d1c8258](https://github.com/foxinmy/weixin4j/commit/4b7ad14df6567064b468b4c9cb7a8bfeff48c8bd)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24819
- https://github.com/foxinmy/weixin4j/pull/229
- https://github.com/foxinmy/weixin4j/commit/d1c825835802cd3a0c04772be1220ff4476ea27c
- https://github.com/foxinmy/weixin4j
