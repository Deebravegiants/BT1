# [M] HTTP Request Smuggling in Netty

## Summary
Severity: Medium
Advisory: GHSA-p2v9-g2qv-p635
CVE: CVE-2019-20445
CWE: CWE-444
Ecosystem: Maven
Published: 2020-02-21
Source: https://github.com/advisories/GHSA-p2v9-g2qv-p635
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler` — affected >=4.0.0 <4.1.45
- Maven: `org.jboss.netty:netty` — affected >=0
- Maven: `io.netty:netty` — affected >=0

## Details
HttpObjectDecoder.java in Netty before 4.1.44 allows a Content-Length header to be accompanied by a second Content-Length header, or by a Transfer-Encoding header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-20445
- https://github.com/netty/netty/issues/9861
- https://github.com/netty/netty/pull/9865
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rce71d33747010d32d31d90f5d737dae26291d96552f513a266c92fbb@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbdb59c683d666130906a9c05a1d2b034c4cc08cda7ed41322bd54fe2@%3Cissues.flume.apache.org%3E
- https://lists.apache.org/thread.html/rb84c57670ec48ef23f4d07973b7fa69f629b8e7fcfb48874362feb6f@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rb5c065e7bd701b0744f9f28ad769943f91745102716c1eb516325f11@%3Cissues.spark.apache.org%3E
- https://lists.apache.org/thread.html/raaac04b7567c554786132144bea3dcb72568edd410c1e6f0101742e7@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/ra9fbfe7d4830ae675bf34c7c0f8c22fc8a4099f65706c1bc4f54c593@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra2ace4bcb5cf487f72cbcbfa0f8cc08e755ec2b93d7e69f276148b08@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra1a71b576a45426af5ee65255be9596ff3181a342f4ba73b800db78f@%3Cdev.geode.apache.org%3E
- https://lists.apache.org/thread.html/r9b20cdac704cf9a583400350e2d5b576fa8417c18ddb961201676c60@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r96e08f929234e8ba1ef4a93a0fd2870f535a1f9ab628fabc46115986@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r959474dcf7f88565ed89f6252ca5a274419006cb71348f14764b183d@%3Ccommits.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/r832724df393a7ef25ca4c7c2eb83ad2d6c21c74569acda5233f9f1ec@%3Ccommits.pulsar.apache.org%3E
- https://access.redhat.com/errata/RHSA-2020:0497
- https://lists.apache.org/thread.html/rd8f72411fb75b98d366400ae789966373b5c3eb3f511e717caf3e49e@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/rdb69125652311d0c41f6066ff44072a3642cf33a4b5e3c4f9c1ec9c2@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/re45ee9256d3233c31d78e59ee59c7dc841c7fbd83d0769285b41e948@%3Ccommits.druid.apache.org%3E
