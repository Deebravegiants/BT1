# [C] jackson-databind vulnerable to deserialization flaw leading to unauthenticated remote code execution

## Summary
Severity: Critical
Advisory: GHSA-h592-38cm-4ggp
CVE: CVE-2017-15095
CWE: CWE-184, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-18
Source: https://github.com/advisories/GHSA-h592-38cm-4ggp
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.8.0 <2.8.11
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.9.0 <2.9.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.0.0 <2.6.7.3
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.7.0 <2.7.9.2

## Details
jackson-databind in versions prior to 2.8.11 and 2.9.4 contain a deserialization flaw which allows an unauthenticated user to perform code execution by sending maliciously crafted input to the readValue method of the ObjectMapper. This issue extends the previous flaw CVE-2017-7525, blacklisting additonal vulnerable classes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15095
- https://github.com/FasterXML/jackson-databind/issues/1680
- https://github.com/FasterXML/jackson-databind/issues/1737
- https://github.com/FasterXML/jackson-databind/commit/a054585e2175ad0882f07bcafedecfac86230f1b
- https://github.com/FasterXML/jackson-databind/commit/a3939d36edcc755c8af55bdc1969e0fa8438f9db
- https://github.com/FasterXML/jackson-databind/commit/ddfddfba6414adbecaff99684ef66eebd3a92e92
- https://github.com/FasterXML/jackson-databind/commit/e865a7a4464da63ded9f4b1a2328ad85c9ded78b
- https://github.com/FasterXML/jackson-databind/commit/e8f043d1aac9b82eee907e0f0c3abbdea723a935
- https://github.com/tolbertam/jackson-databind/commit/80566a0f96b2003863f9d8f9ccc3b562001e147b
- https://access.redhat.com/errata/RHSA-2017:3189
- https://lists.apache.org/thread.html/f095a791bda6c0595f691eddd0febb2d396987eec5cbd29120d8c629@%3Csolr-user.lucene.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/01/msg00037.html
- https://security.netapp.com/advisory/ntap-20171214-0003
- https://web.archive.org/web/20200401000000*/http://www.securityfocus.com/bid/103880
- https://web.archive.org/web/20201221192044/http://www.securitytracker.com/id/1039769
- https://www.debian.org/security/2017/dsa-4037
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://access.redhat.com/errata/RHSA-2017:3190
