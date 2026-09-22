# [H] Code execution vulnerability in HtmlUnit

## Summary
Severity: High
Advisory: GHSA-5mh9-r3rr-9597
CVE: CVE-2020-5529
CWE: CWE-665, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-21
Source: https://github.com/advisories/GHSA-5mh9-r3rr-9597
Type: github-advisory

## Affected
- Maven: `net.sourceforge.htmlunit:htmlunit` — affected >=0 <2.37.0

## Details
HtmlUnit prior to 2.37.0 contains code execution vulnerabilities. HtmlUnit initializes Rhino engine improperly, hence a malicious JavScript code can execute arbitrary Java code on the application. Moreover, when embedded in Android application, Android-specific initialization of Rhino engine is done in an improper way, hence a malicious JavaScript code can execute arbitrary Java code on the application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5529
- https://github.com/HtmlUnit/htmlunit/commit/bc1f58d483cc8854a9c4c1739abd5e04a2eb0367
- https://github.com/HtmlUnit/htmlunit
- https://github.com/HtmlUnit/htmlunit/releases/tag/2.37.0
- https://jvn.jp/en/jp/JVN34535327
- https://lists.apache.org/thread.html/ra2cd7f8e61dc6b8a2d9065094cd1f46aa63ad10f237ee363e26e8563%40%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/ra2cd7f8e61dc6b8a2d9065094cd1f46aa63ad10f237ee363e26e8563@%3Ccommits.camel.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/08/msg00023.html
- https://usn.ubuntu.com/4584-1
