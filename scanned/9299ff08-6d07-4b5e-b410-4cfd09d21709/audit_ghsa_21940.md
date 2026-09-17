# [C] Serialization vulnerability in Apache Tapestry

## Summary
Severity: Critical
Advisory: GHSA-c566-2grg-mjwg
CVE: CVE-2020-17531
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-c566-2grg-mjwg
Type: github-advisory

## Affected
- Maven: `org.apache.tapestry:tapestry-project` — affected >=4.0 <5.0.1

## Details
A Java Serialization vulnerability was found in Apache Tapestry 4. Apache Tapestry 4 will attempt to deserialize the "sp" parameter even before invoking the page's validate method, leading to deserialization without authentication. Apache Tapestry 4 reached end of life in 2008 and no update to address this issue will be released. Apache Tapestry 5 versions are not vulnerable to this issue. Users of Apache Tapestry 4 should upgrade to the latest Apache Tapestry 5 version.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-17531
- https://lists.apache.org/thread.html/r700a6aa234dbff0555d4187bdc8274d7e4c0afbf35b9a3457f09ee76%40%3Cusers.tapestry.apache.org%3E
- https://lists.apache.org/thread.html/r700a6aa234dbff0555d4187bdc8274d7e4c0afbf35b9a3457f09ee76@%3Cusers.tapestry.apache.org%3E
- https://security.netapp.com/advisory/ntap-20210115-0007
- http://www.openwall.com/lists/oss-security/2022/12/02/1
