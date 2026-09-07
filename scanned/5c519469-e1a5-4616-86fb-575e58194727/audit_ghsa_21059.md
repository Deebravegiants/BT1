# [C] Java Melody vulnerable to cross-site scripting

## Summary
Severity: Critical
Advisory: GHSA-cqhr-jqvc-qw9p
CVE: CVE-2016-1000273
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-20
Source: https://github.com/advisories/GHSA-cqhr-jqvc-qw9p
Type: github-advisory

## Affected
- Maven: `net.bull.javamelody:javamelody-core` — affected >=0 <1.61.0

## Details
JavaMelody is a monitoring tool for JavaEE applications. Versions prior to 1.61.0 are vulnerable to a cross-site scripting (XSS) attack. This issue was patched in version 1.61.0, and users are recommended to upgrade to the latest version. There are no known workarounds.

## References
- https://github.com/javamelody/javamelody/commit/e0497c1980acebd257d3da78dfde29ae9bdffdf6
- https://github.com/javamelody/javamelody
- https://github.com/javamelody/javamelody/wiki/ReleaseNotes#1620
