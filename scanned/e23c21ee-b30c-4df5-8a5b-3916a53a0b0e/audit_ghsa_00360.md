# [M] Improper Validation of Certificates in apache axis

## Summary
Severity: Medium
Advisory: GHSA-r53v-vm87-f72c
CVE: CVE-2014-3596
CWE: CWE-297
Ecosystem: Maven
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-r53v-vm87-f72c
Type: github-advisory

## Affected
- Maven: `org.apache.axis:axis` — affected >=0
- Maven: `axis:axis` — affected >=0

## Details
The getCN function in Apache Axis 1.4 and earlier does not properly verify that the server hostname matches a domain name in the subject's Common Name (CN) or subjectAltName field of the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via a certificate with a subject that specifies a common name in a field that is not the CN field.  NOTE: this issue exists because of an incomplete fix for CVE-2012-5784.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3596
- https://www.oracle.com/security-alerts/cpujan2020.html
- https://web.archive.org/web/20200227173427/http://www.securityfocus.com/bid/69295
- https://web.archive.org/web/20160815194947/http://www.securitytracker.com/id/1030745
- https://lists.apache.org/thread.html/de2af12dcaba653d02b03235327ca4aa930401813a3cced8e151d29c@%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/de2af12dcaba653d02b03235327ca4aa930401813a3cced8e151d29c%40%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/a308887782e05da7cf692e4851ae2bd429a038570cbf594e6631cc8d@%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/a308887782e05da7cf692e4851ae2bd429a038570cbf594e6631cc8d%40%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/8aa25c99eeb0693fc229ec87d1423b5ed5d58558618706d8aba1d832@%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/8aa25c99eeb0693fc229ec87d1423b5ed5d58558618706d8aba1d832%40%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/5e6c92145deddcecf70c3604041dcbd615efa2d37632fc2b9c367780@%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/5e6c92145deddcecf70c3604041dcbd615efa2d37632fc2b9c367780%40%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/44d4e88a5fa8ae60deb752029afe9054da87c5f859caf296fcf585e5@%3Cjava-dev.axis.apache.org%3E
- https://lists.apache.org/thread.html/44d4e88a5fa8ae60deb752029afe9054da87c5f859caf296fcf585e5%40%3Cjava-dev.axis.apache.org%3E
- https://issues.apache.org/jira/browse/AXIS-2905
- https://exchange.xforce.ibmcloud.com/vulnerabilities/95377
- https://bugzilla.redhat.com/show_bug.cgi?id=1129935
- https://access.redhat.com/security/cve/CVE-2014-3596
- https://access.redhat.com/errata/RHSA-2015:1010
- https://access.redhat.com/errata/RHSA-2014:1193
