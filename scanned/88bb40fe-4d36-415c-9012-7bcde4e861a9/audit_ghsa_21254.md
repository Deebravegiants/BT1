# [C] Arbitrary code execution in Apache Commons Text

## Summary
Severity: Critical
Advisory: GHSA-599f-7c49-w659
CVE: CVE-2022-42889
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-13
Source: https://github.com/advisories/GHSA-599f-7c49-w659
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-text` — affected >=1.5 <1.10.0
- Maven: `com.guicedee.services:commons-text` — affected >=0

## Details
Apache Commons Text performs variable interpolation, allowing properties to be dynamically evaluated and expanded. The standard format for interpolation is "${prefix:name}", where "prefix" is used to locate an instance of org.apache.commons.text.lookup.StringLookup that performs the interpolation. Starting with version 1.5 and continuing through 1.9, the set of default Lookup instances included interpolators that could result in arbitrary code execution or contact with remote servers. These lookups are: - "script" - execute expressions using the JVM script execution engine (javax.script) - "dns" - resolve dns records - "url" - load values from urls, including from remote servers Applications using the interpolation defaults in the affected versions may be vulnerable to remote code execution or unintentional contact with remote servers if untrusted configuration values are used. Users are recommended to upgrade to Apache Commons Text 1.10.0, which disables the problematic interpolators by default.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-42889
- https://arxiv.org/pdf/2306.05534
- https://github.com/apache/commons-text
- https://lists.apache.org/thread/n2bd4vdsgkqh2tm14l1wyc3jyol7s1om
- https://psirt.global.sonicwall.com/vuln-detail/SNWLID-2022-0022
- https://security.gentoo.org/glsa/202301-05
- https://security.netapp.com/advisory/ntap-20221020-0004
- https://securitylab.github.com/advisories/GHSL-2022-018_Apache_Commons_Text
- http://packetstormsecurity.com/files/171003/OX-App-Suite-Cross-Site-Scripting-Server-Side-Request-Forgery.html
- http://packetstormsecurity.com/files/176650/Apache-Commons-Text-1.9-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2023/Feb/3
- http://www.openwall.com/lists/oss-security/2022/10/13/4
- http://www.openwall.com/lists/oss-security/2022/10/18/1
