# [M] Sensitive Data Exposure in Apache Ant

## Summary
Severity: Medium
Advisory: GHSA-4p6w-m9wc-c9c9
CVE: CVE-2020-1945
CWE: CWE-200, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2020-09-14
Source: https://github.com/advisories/GHSA-4p6w-m9wc-c9c9
Type: github-advisory

## Affected
- Maven: `org.apache.ant:ant` — affected >=1.1 <1.9.15
- Maven: `org.apache.ant:ant` — affected >=1.10.0 <1.10.8

## Details
Apache Ant 1.1 to 1.9.14 and 1.10.0 to 1.10.7 uses the default temporary directory identified by the Java system property java.io.tmpdir for several tasks and may thus leak sensitive information. The fixcrlf and replaceregexp tasks also copy files from the temporary directory back into the build tree allowing an attacker to inject modified source files into the build process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-1945
- https://lists.apache.org/thread.html/raaeddc41da8f3afb1cb224876084a45f68e437a0afd9889a707e4b0c@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rb860063819b9c0990e1fbce29d83f4554766fe5a05e3b3939736bf2b@%3Ccommits.myfaces.apache.org%3E
- https://lists.apache.org/thread.html/rb8ec556f176c83547b959150e2108e2ddf1d61224295941908b0a81f@%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rbfe9ba28b74f39f46ec1bbbac3bef313f35017cf3aac13841a84483a@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rc3c8ef9724b5b1e171529b47f4b35cb7920edfb6e917fa21eb6c64ea@%3Cdev.ant.apache.org%3E
- https://lists.apache.org/thread.html/rc89e491b5b270fb40f1210b70554527b737c217ad2e831b643ead6bc@%3Cuser.ant.apache.org%3E
- https://lists.apache.org/thread.html/rce099751721c26a8166d8b6578293820832831a0b2cb8d93b8efa081@%3Cnotifications.groovy.apache.org%3E
- https://lists.apache.org/thread.html/rd7dda48ff835f4d0293949837d55541bfde3683bd35bd8431e324538@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rda80ac59119558eaec452e58ddfac2ccc9211da1c65f7927682c78b1@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rdaa9c51d5dc6560c9d2b3f3d742c768ad0705e154041e574a0fae45c@%3Cnotifications.groovy.apache.org%3E
- https://lists.apache.org/thread.html/re1ce84518d773a94a613d988771daf9252c9cf7375a9a477009f9735@%3Ccommits.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rf07feaf78afc8f701e21948a06ef92565d3dff1242d710f4fbf900b2@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/rfd346609527a79662c48b1da3ac500ec30f29f7ddaa3575051e81890@%3Ccommits.creadur.apache.org%3E
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EQBR65TINSJRN7PTPIVNYS33P535WM74
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RRVAWTCVXJMRYKQKEXYSNBF7NLSR6OEI
- https://security.gentoo.org/glsa/202007-34
- https://usn.ubuntu.com/4380-1
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
