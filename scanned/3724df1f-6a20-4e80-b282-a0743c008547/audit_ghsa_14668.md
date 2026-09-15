# [M] QOS.CH logback-core Expression Language Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pr98-23f8-jwxv
CVE: CVE-2024-12798
CWE: CWE-917
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:L/VI:H/VA:L/SC:L/SI:H/SA:L/RE:L/U:Clear (CVSS_V4)
Published: 2024-12-19
Source: https://github.com/advisories/GHSA-pr98-23f8-jwxv
Type: github-advisory

## Affected
- Maven: `ch.qos.logback:logback-core` — affected >=1.4.0 <1.5.13
- Maven: `ch.qos.logback:logback-core` — affected >=0 <1.3.15

## Details
ACE vulnerability in JaninoEventEvaluator by QOS.CH logback-core up to and including version 1.5.12 in Java applications allows attackers to execute arbitrary code by compromising an existing logback configuration file or by injecting an environment variable before program execution.

Malicious logback configuration files can allow the attacker to execute arbitrary code using the JaninoEventEvaluator extension.

A successful attack requires the user to have write access to a configuration file. Alternatively, the attacker could inject a malicious environment variable pointing to a malicious configuration file. In both cases, the attack requires existing privilege.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12798
- https://github.com/qos-ch/logback/commit/2cb6d520df7592ef1c3a198f1b5df3c10c93e183
- https://github.com/qos-ch/logback
- https://logback.qos.ch/news.html#1.3.15
- https://logback.qos.ch/news.html#1.5.13
