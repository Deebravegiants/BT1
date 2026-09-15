# [H] CVE-2020-11620

## Summary
Severity: High
Advisory: CVE-2020-11620
Aliases: GHSA-h4rc-386g-6m85
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-07
Source: https://osv.dev/vulnerability/CVE-2020-11620
Type: osv

## Details
FasterXML jackson-databind 2.x before 2.9.10.4 mishandles the interaction between serialization gadgets and typing, related to org.apache.commons.jelly.impl.Embedded (aka commons-jelly).

## References
- https://lists.apache.org/thread.html/rf1bbc0ea4a9f014cf94df9a12a6477d24a27f52741dbc87f2fd52ff2%40%3Cissues.geode.apache.org%3E
- https://medium.com/%40cowtowncoder/on-jackson-cves-dont-panic-here-is-what-you-need-to-know-54cd0d6e8062
- https://lists.debian.org/debian-lts-announce/2020/04/msg00012.html
- https://security.netapp.com/advisory/ntap-20200511-0004/
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://github.com/FasterXML/jackson-databind/issues/2682
