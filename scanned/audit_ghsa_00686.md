# [H] Denial of Service in Netty

## Summary
Severity: High
Advisory: GHSA-mm9x-g8pc-w292
CVE: CVE-2020-11612
CWE: CWE-119, CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-06-15
Source: https://github.com/advisories/GHSA-mm9x-g8pc-w292
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler` — affected >=4.1.0 <4.1.46

## Details
The ZlibDecoders in Netty 4.1.x before 4.1.46 allow for unbounded memory allocation while decoding a ZlibEncoded byte stream. An attacker could send a large ZlibEncoded byte stream to the Netty server, forcing the server to allocate all of its free memory to a single decoder.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11612
- https://github.com/netty/netty/issues/6168
- https://github.com/netty/netty/pull/9924
- https://lists.apache.org/thread.html/r9c30b7fca4baedebcb46d6e0f90071b30cc4a0e074164d50122ec5ec@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra98e3a8541a09271f96478d5e22c7e3bd1afdf48641c8be25d62d9f9@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/raaac04b7567c554786132144bea3dcb72568edd410c1e6f0101742e7@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/rd302ddb501fa02c5119120e5fc21df9a1c00e221c490edbe2d7ad365@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rdb69125652311d0c41f6066ff44072a3642cf33a4b5e3c4f9c1ec9c2@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/re1ea144e91f03175d661b2d3e97c7d74b912e019613fa90419cf63f4@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ref2c8a0cbb3b8271e5b9a06457ba78ad2028128627186531730f50ef@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ref3943adbc3a8813aee0e3a9dd919bacbb27f626be030a3c6d6c7f83@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rf5b2dfb7401666a19915f8eaef3ba9f5c3386e2066fcd2ae66e16a2f@%3Cdev.flink.apache.org%3E
- https://lists.apache.org/thread.html/rf803b65b4a57589d79cf2e83d8ece0539018d32864f932f63c972844@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rf9f8bcc4ca8d2788f77455ff594468404732a4497baebe319043f4d5@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rfd173eac20d5e5f581c8984b685c836dafea8eb2f7ff85f617704cf1@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rff8859c0d06b1688344b39097f9685c43b461cf2bc41f60f001704e9@%3Ccommits.zookeeper.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/09/msg00003.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TS6VX7OMXPDJIU5LRGUAHRK6MENAVJ46
- https://security.netapp.com/advisory/ntap-20201223-0001
- https://www.debian.org/security/2021/dsa-4885
