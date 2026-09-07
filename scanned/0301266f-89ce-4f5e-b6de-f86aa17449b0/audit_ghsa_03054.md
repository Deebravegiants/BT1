# [H] Code injection in Apache Ant

## Summary
Severity: High
Advisory: GHSA-f62v-xpxf-3v68
CVE: CVE-2020-11979
CWE: CWE-74, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-02-03
Source: https://github.com/advisories/GHSA-f62v-xpxf-3v68
Type: github-advisory

## Affected
- Maven: `org.apache.ant:ant` — affected >=0 <1.10.9

## Details
As mitigation for CVE-2020-1945 Apache Ant 1.10.8 changed the permissions of temporary files it created so that only the current user was allowed to access them. Unfortunately the fixcrlf task deleted the temporary file and created a new one without said protection, effectively nullifying the effort. This would still allow an attacker to inject modified source files into the build process.

## References
- https://github.com/gradle/gradle/security/advisories/GHSA-j45w-qrgf-25vm
- https://nvd.nist.gov/vuln/detail/CVE-2020-11979
- https://github.com/apache/ant/commit/87ac51d3c22bcf7cfd0dc07cb0bd04a496e0d428
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://security.gentoo.org/glsa/202011-18
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/U3NRQQ7ECII4ZNGW7GBC225LVYMPQEKB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DYBRN5C2RW7JRY75IB7Q7ZVKZCHWAQWS
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AALW42FWNQ35F7KB3JVRC6NBVV7AAYYI
- https://lists.apache.org/thread.html/rc3c8ef9724b5b1e171529b47f4b35cb7920edfb6e917fa21eb6c64ea%40%3Cdev.ant.apache.org%3E
- https://lists.apache.org/thread.html/rbfe9ba28b74f39f46ec1bbbac3bef313f35017cf3aac13841a84483a@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/raaeddc41da8f3afb1cb224876084a45f68e437a0afd9889a707e4b0c@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/r5e1cdd79f019162f76414708b2092acad0a6703d666d72d717319305@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/r4ca33fad3fb39d130cda287d5a60727d9e706e6f2cf2339b95729490@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/r2306b67f20c24942b872b0a41fbdc9330e8467388158bcd19c1094e0@%3Cdev.creadur.apache.org%3E
- https://lists.apache.org/thread.html/r1dc8518dc99c42ecca5ff82d0d2de64cd5d3a4fa691eb9ee0304781e@%3Cdev.creadur.apache.org%3E
