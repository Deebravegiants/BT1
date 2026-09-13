# [H] Regular expression denial of service in Apache ShenYu

## Summary
Severity: High
Advisory: GHSA-cw56-j3fm-7w57
CVE: CVE-2022-26650
CWE: CWE-1333, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-cw56-j3fm-7w57
Type: github-advisory

## Affected
- Maven: `org.apache.shenyu:shenyu` — affected >=2.4.0 <2.4.3
- Maven: `org.apache.shenyu:shenyu-bootstrap` — affected >=2.4.0 <2.4.3

## Details
In Apache ShenYui, ShenYu-Bootstrap, RegexPredicateJudge.java uses Pattern.matches(conditionData.getParamValue(), realData) to make judgments, where both parameters are controllable by the user. This can cause an attacker pass in malicious regular expressions and characters causing a resource exhaustion. This issue affects Apache ShenYu (incubating) 2.4.0, 2.4.1 and 2.4.2 and is fixed in 2.4.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-26650
- https://github.com/apache/incubator-shenyu
- https://lists.apache.org/thread/8rp33m3nm4bwtx3qx76mqynth3t3d673
- http://www.openwall.com/lists/oss-security/2022/05/17/3
