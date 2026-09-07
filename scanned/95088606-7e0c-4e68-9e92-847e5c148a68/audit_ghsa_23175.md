# [M] Apache QPID Allows Remote Authentication Bypass

## Summary
Severity: Medium
Advisory: GHSA-phw8-fw9g-v3xc
CVE: CVE-2012-3467
CWE: CWE-287
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-phw8-fw9g-v3xc
Type: github-advisory

## Affected
- Maven: `org.apache.qpid:qpid-parent` — affected >=0 <0.17

## Details
Apache QPID 0.14, 0.16, and earlier uses a NullAuthenticator mechanism to authenticate catch-up shadow connections to AMQP brokers, which allows remote attackers to bypass authentication.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3467
- https://bugzilla.redhat.com/show_bug.cgi?id=836276
- https://exchange.xforce.ibmcloud.com/vulnerabilities/77568
- https://github.com/apache/qpid
- https://issues.apache.org/jira/browse/QPID-3849
- https://web.archive.org/web/20200229113556/http://www.securityfocus.com/bid/54954
- http://rhn.redhat.com/errata/RHSA-2012-1277.html
- http://rhn.redhat.com/errata/RHSA-2012-1279.html
- http://svn.apache.org/viewvc?view=revision&revision=1352992
- http://www.openwall.com/lists/oss-security/2012/08/09/6
