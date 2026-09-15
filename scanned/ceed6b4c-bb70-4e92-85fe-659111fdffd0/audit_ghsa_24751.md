# [H] Loop with Unreachable Exit Condition in Apache Thrift

## Summary
Severity: High
Advisory: GHSA-rj7p-rfgp-852x
CVE: CVE-2019-0205
CWE: CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rj7p-rfgp-852x
Type: github-advisory

## Affected
- Maven: `org.apache.thrift:libthrift` — affected >=0 <0.13.0

## Details
In Apache Thrift all versions up to and including 0.12.0, a server or client may run into an endless loop when feed with specific input data. Because the issue had already been partially fixed in version 0.11.0, depending on the installed version it affects only certain language bindings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-0205
- https://lists.apache.org/thread.html/r4633082b834eebccd0d322697651d931ab10ca9c51ee7ef18e1f60f4@%3Cdev.thrift.apache.org%3E
- https://lists.apache.org/thread.html/r4d3f1d3e333d9c2b2f6e6ae8ed8750d4de03410ac294bcd12c7eefa3@%3Ccommits.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/r50bf84c60867574238d18cdad5da9f303b618114c35566a3a001ae08@%3Cdev.hive.apache.org%3E
- https://lists.apache.org/thread.html/r53c03e1c979b9c628d0d65e0f49dd9a9f9d7572838727ad11b750575@%3Cuser.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/r55609613abab203a1f2c1f3de050b63ae8f5c4a024df0d848d6915ff@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r569b2b3da41ff45bfacfca6787a4a8728edd556e185b69b140181d9d@%3Cdev.thrift.apache.org%3E
- https://lists.apache.org/thread.html/r573029c2f8632e3174b9eea7cd57f9c9df33f2f706450e23fc57750a@%3Ccommits.thrift.apache.org%3E
- https://lists.apache.org/thread.html/r67a704213d13326771f46c84bbd84c8281bb93946e155e0e40abcb4c@%3Ccommits.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/r73a3c8b80765e3d2430ff51f22b778d0c917919f01815b69ed16cf9d@%3Cissues.hive.apache.org%3E
- https://lists.apache.org/thread.html/r7859e767c90c8f4971dec50f801372aa64e88f143c3e8a265a36f9b4@%3Cuser.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/r92b7771afee2625209c36727fefdc77033964e9a1daa81ec3327e625@%3Cuser.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/r934f312dd5add7276ac2de684d8b237554ff9f34479a812df5fd6aee@%3Ccommits.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/rab740e5c70424ef79fd095a4b076e752109aeee41c4256c2e5e5e142@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rb139fa1d2714822d8c6e6f3bd6f5d5c91844d313201185c409288fd9@%3Ccommits.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/rba61c1f3a3b1960a6a694775b1a437751eba0825f30188f69387fe90@%3Cdev.thrift.apache.org%3E
- https://lists.apache.org/thread.html/rce0d368a78b42c545f26c2e6e91e2b8a91b27b60d0cb45fe1911d337@%3Cnotifications.thrift.apache.org%3E
- https://lists.apache.org/thread.html/re387dc6ca11cb0b0ce4de8e800bb91ca50fee054b80105f5cd34adcb@%3Cdev.thrift.apache.org%3E
- https://lists.apache.org/thread.html/rf359e5cc6a185494fc0cfe837fe82f7db2ef49242d35cbf3895aebce@%3Cdev.thrift.apache.org%3E
- https://security.gentoo.org/glsa/202107-32
