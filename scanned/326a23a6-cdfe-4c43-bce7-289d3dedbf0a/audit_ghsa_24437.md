# [H] Denial of service in Apache Mesos

## Summary
Severity: High
Advisory: GHSA-x869-784m-jmj2
CVE: CVE-2017-7687
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-x869-784m-jmj2
Type: github-advisory

## Affected
- Maven: `org.apache.mesos:mesos` — affected >=0 <1.1.3
- Maven: `org.apache.mesos:mesos` — affected >=1.2.0 <1.2.2
- Maven: `org.apache.mesos:mesos` — affected >=1.3.0 <1.3.1

## Details
When handling a decoding failure for a malformed URL path of an HTTP request, libprocess in Apache Mesos might crash because the code accidentally calls inappropriate function. A malicious actor can therefore cause a denial of service of Mesos masters rendering the Mesos-controlled cluster inoperable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7687
- https://lists.apache.org/thread.html/2c9ed2b07c2b2831a11d21db3cf8408a71fcf2c300d73ca01bad89df@%3Cdev.mesos.apache.org%3E
- http://www.securityfocus.com/bid/101027
