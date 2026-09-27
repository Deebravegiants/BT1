# [M] Man-in-the-middle attack in Apache Cassandra

## Summary
Severity: Medium
Advisory: GHSA-24ww-mc5x-xc43
CVE: CVE-2020-13946
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-24ww-mc5x-xc43
Type: github-advisory

## Affected
- Maven: `org.apache.cassandra:cassandra-all` — affected >=2.1.0 <2.1.12
- Maven: `org.apache.cassandra:cassandra-all` — affected >=2.2.0 <2.2.18
- Maven: `org.apache.cassandra:cassandra-all` — affected >=3.0.0 <3.0.22
- Maven: `org.apache.cassandra:cassandra-all` — affected >=3.11.0 <3.11.8
- Maven: `org.apache.cassandra:cassandra-all` — affected >=4.0-beta1 <4.0-beta2

## Details
In Apache Cassandra, all versions prior to 2.1.22, 2.2.18, 3.0.22, 3.11.8 and 4.0-beta2, it is possible for a local attacker without access to the Apache Cassandra process or configuration files to manipulate the RMI registry to perform a man-in-the-middle attack and capture user names and passwords used to access the JMX interface. The attacker can then use these credentials to access the JMX interface and perform unauthorised operations. Users should also be aware of CVE-2019-2684, a JRE vulnerability that enables this issue to be exploited remotely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-13946
- https://lists.apache.org/thread.html/r1fd117082b992e7d43c1286e966c285f98aa362e685695d999ff42f7@%3Cuser.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/r718e01f61b35409a4f7a3ccbc1cb5136a1558a9f9c2cb8d4ca9be1ce@%3Cuser.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/rab8d90d28f944d84e4d7852f355a25c89451ae02c2decc4d355a9cfc@%3Cuser.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/rcd7544b24d8fc32b7950ec4c117052410b661babaa857fb1fc641152%40%3Cuser.cassandra.apache.org%3E
- https://security.netapp.com/advisory/ntap-20210521-0005
