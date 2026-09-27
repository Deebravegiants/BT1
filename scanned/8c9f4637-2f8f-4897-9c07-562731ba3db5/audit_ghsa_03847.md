# [H] Denial of Service in Apache Commons Compress

## Summary
Severity: High
Advisory: GHSA-53x6-4x5p-rrvv
CVE: CVE-2019-12402
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-10-11
Source: https://github.com/advisories/GHSA-53x6-4x5p-rrvv
Type: github-advisory

## Affected
- Maven: `org.apache.commons:commons-compress` — affected >=1.15 <1.19
- Maven: `io.github.1tchy.java9modular.org.apache.commons:commons-compress` — affected 1.18.1

## Details
The file name encoding algorithm used internally in Apache Commons Compress 1.15 to 1.18 can get into an infinite loop when faced with specially crafted inputs. This can lead to a denial of service attack if an attacker can choose the file names inside of an archive created by Compress.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12402
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpujul2020.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuapr2020.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://security.netapp.com/advisory/ntap-20230818-0001
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WZB3GB7YXIOUKIOQ27VTIP6KKGJJ3CKL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QLJIK2AUOZOWXR3S5XXBUNMOF3RTHTI7
- https://lists.apache.org/thread.html/rf5230a049d989dbfdd404b4320a265dceeeba459a4d04ec21873bd55@%3Csolr-user.lucene.apache.org%3E
- https://lists.apache.org/thread.html/re13bd219dd4b651134f6357f12bd07a0344eea7518c577bbdd185265@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/rdebc1830d6c09c11d5a4804ca26769dbd292d17d361c61dea50915f0@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/rd3f99d732baed459b425fb0a9e9e14f7843c9459b12037e4a9d753b5@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/rcc35ab6be300365de5ff9587e0479d10d7d7c79070921837e3693162@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r972f82d821b805d04602976a9736c01b6bf218cfe0c3f48b472db488@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/r7af60fbd8b2350d49d14e53a3ab2801998b9d1af2d6fcac60b060a53@%3Cdev.brooklyn.apache.org%3E
- https://lists.apache.org/thread.html/r5caf4fcb69d2749225391e61db7216282955204849ba94f83afe011f@%3Cissues.flink.apache.org%3E
