# [M] QOS.CH logback-core is vulnerable to Arbitrary Code Execution through file processing

## Summary
Severity: Medium
Advisory: GHSA-25qh-j22f-pwp8
CVE: CVE-2025-11226
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:H/UI:P/VC:H/VI:L/VA:L/SC:H/SI:L/SA:L (CVSS_V4)
Published: 2025-10-01
Source: https://github.com/advisories/GHSA-25qh-j22f-pwp8
Type: github-advisory

## Affected
- Maven: `ch.qos.logback:logback-core` — affected >=1.4.0 <1.5.19
- Maven: `ch.qos.logback:logback-core` — affected >=0 <1.3.16

## Details
QOS.CH logback-core versions up to 1.5.18 contain an ACE vulnerability in conditional configuration file processing in Java applications. This vulnerability allows an attacker to execute arbitrary code by compromising an existing logback configuration file or by injecting a malicious environment variable before program execution.

A successful attack requires the Janino library and Spring Framework to be present on the user's class path. Additionally, the attacker must have write access to a configuration file. Alternatively, the attacker could inject a malicious environment variable pointing to a malicious configuration file. In both cases, the attack requires existing privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11226
- https://github.com/qos-ch/logback/issues/974
- https://github.com/qos-ch/logback/commit/61f6a2544f36b3016e0efd434ee21f19269f1df7
- https://github.com/qos-ch/logback
- https://github.com/qos-ch/logback/releases/tag/v_1.5.19
- https://logback.qos.ch/news.html#1.3.16
- https://logback.qos.ch/news.html#1.5.19
