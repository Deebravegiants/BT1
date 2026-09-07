# [H] Improper Input Validation in BeanShell

## Summary
Severity: High
Advisory: GHSA-gxg6-rc6c-v673
CVE: CVE-2016-2510
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gxg6-rc6c-v673
Type: github-advisory

## Affected
- Maven: `org.apache-extras.beanshell:bsh` — affected >=0 <2.0b6

## Details
BeanShell (bsh) before 2.0b6, when included on the classpath by an application that uses Java serialization or XStream, allows remote attackers to execute arbitrary code via crafted serialized data, related to XThis.Handler.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2510
- https://github.com/frohoff/ysoserial/pull/13
- https://github.com/beanshell/beanshell/commit/1ccc66bb693d4e46a34a904db8eeff07808d2ced
- https://github.com/beanshell/beanshell/commit/7c68fde2d6fc65e362f20863d868c112a90a9b49
- https://access.redhat.com/errata/RHSA-2016:1135
- https://access.redhat.com/errata/RHSA-2016:1376
- https://access.redhat.com/errata/RHSA-2019:1545
- https://github.com/beanshell/beanshell/releases/tag/2.0b6
- https://security.gentoo.org/glsa/201607-17
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.rsaconference.com/writable/presentations/file_upload/asd-f03-serial-killer-silently-pwning-your-java-endpoints.pdf
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00056.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00078.html
- http://rhn.redhat.com/errata/RHSA-2016-0539.html
- http://rhn.redhat.com/errata/RHSA-2016-0540.html
- http://rhn.redhat.com/errata/RHSA-2016-2035.html
- http://www.debian.org/security/2016/dsa-3504
- http://www.ubuntu.com/usn/USN-2923-1
