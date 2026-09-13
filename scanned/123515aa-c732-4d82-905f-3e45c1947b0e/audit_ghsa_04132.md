# [M] Moderate severity vulnerability that affects com.puppycrawl.tools:checkstyle

## Summary
Severity: Medium
Advisory: GHSA-gp32-7h29-rpxm
CVE: CVE-2019-9658
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-03-14
Source: https://github.com/advisories/GHSA-gp32-7h29-rpxm
Type: github-advisory

## Affected
- Maven: `com.puppycrawl.tools:checkstyle` — affected >=0 <8.18

## Details
Checkstyle prior to 8.18 loads external DTDs by default, which can potentially lead to denial of service attacks or the leaking of confidential information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9658
- https://github.com/checkstyle/checkstyle/issues/6474
- https://github.com/checkstyle/checkstyle/issues/6478
- https://github.com/checkstyle/checkstyle/pull/6476
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VJPT54USMGWT3Y6XVXLDEHKRUY2EI4OE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/AEYBAHYAV37WHMOXZYM2ZWF46FHON6YC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2BMOPJ2XYE4LB2HM7OMSUBBIYEDUTLWE
- https://lists.debian.org/debian-lts-announce/2019/04/msg00029.html
- https://lists.apache.org/thread.html/rda99599896c3667f2cc9e9d34c7b6ef5d2bbed1f4801e1d75a2b0679@%3Ccommits.nifi.apache.org%3E
- https://lists.apache.org/thread.html/fff26ee7b59360a0264fef4e8ed9454ef652db2c39f2892a9ea1c9cb@%3Cnotifications.fluo.apache.org%3E
- https://lists.apache.org/thread.html/a35a8ccb316d4c2340710f610cba8058e87d5376259b35ef3ed2bf89@%3Cnotifications.accumulo.apache.org%3E
- https://lists.apache.org/thread.html/994221405e940e148adcfd9cb24ffc6700bed70c7820c55a22559d26@%3Cnotifications.fluo.apache.org%3E
- https://lists.apache.org/thread.html/7eea10e7be4c21060cb1e79f6524c6e6559ba833b1465cd2870a56b9@%3Cserver-dev.james.apache.org%3E
- https://lists.apache.org/thread.html/6bf8bbbca826e883f09ba40bc0d319350e1d6d4cf4df7c9e399b2699@%3Ccommits.fluo.apache.org%3E
- https://github.com/checkstyle/checkstyle
- https://github.com/advisories/GHSA-gp32-7h29-rpxm
- https://checkstyle.org/releasenotes.html#Release_8.18
