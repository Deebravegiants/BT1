# [C] CVE-2019-20444

## Summary
Severity: Critical
Advisory: CVE-2019-20444
Aliases: GHSA-cqqj-4p63-rrmm
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-01-29
Source: https://osv.dev/vulnerability/CVE-2019-20444
Type: osv

## Details
HttpObjectDecoder.java in Netty before 4.1.44 allows an HTTP header that lacks a colon, which might be interpreted as a separate header with an incorrect syntax, or might be interpreted as an "invalid fold."

## References
- https://github.com/poc-effectiveness/PoCAdaptation/tree/main/Adapted/CVE-2019-20444/5.0.0.Alpha1/exploit
- https://lists.apache.org/thread.html/r059b042bca47be53ff8a51fd04d95eb01bb683f1afa209db136e8cb7%40%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r059b042bca47be53ff8a51fd04d95eb01bb683f1afa209db136e8cb7@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r0aa8b28e76ec01c697b15e161e6797e88fc8d406ed762e253401106e%40%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/r0aa8b28e76ec01c697b15e161e6797e88fc8d406ed762e253401106e@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/r0c3d49bfdbc62fd3915676433cc5899c5506d06da1c552ef1b7923a5%40%3Ccommon-issues.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/r0c3d49bfdbc62fd3915676433cc5899c5506d06da1c552ef1b7923a5@%3Ccommon-issues.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/r0f5e72d5f69b4720dfe64fcbc2da9afae949ed1e9cbffa84bb7d92d7%40%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r0f5e72d5f69b4720dfe64fcbc2da9afae949ed1e9cbffa84bb7d92d7@%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/r1b103833cb5bc8466e24ff0ecc5e75b45a705334ab6a444e64e840a0@%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/r1fcccf8bdb3531c28bc9aa605a6a1bea7e68cef6fc12e01faafb2fb5%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r1fcccf8bdb3531c28bc9aa605a6a1bea7e68cef6fc12e01faafb2fb5@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r205937c85817a911b0c72655c2377e7a2c9322d6ef6ce1b118d34d8d%40%3Cdev.geode.apache.org%3E
- https://lists.apache.org/thread.html/r205937c85817a911b0c72655c2377e7a2c9322d6ef6ce1b118d34d8d@%3Cdev.geode.apache.org%3E
- https://lists.apache.org/thread.html/r2f2989b7815d809ff3fda8ce330f553e5f133505afd04ffbc135f35f%40%3Cissues.spark.apache.org%3E
- https://lists.apache.org/thread.html/r2f2989b7815d809ff3fda8ce330f553e5f133505afd04ffbc135f35f@%3Cissues.spark.apache.org%3E
- https://lists.apache.org/thread.html/r310d2ce22304d5298ff87f10134f918c87919b452734f9841d95682d%40%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r310d2ce22304d5298ff87f10134f918c87919b452734f9841d95682d@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r34912a9b1a5c269a77b8be94ef6fb6d1e9b3c69129719dc00f01cf0b%40%3Cdev.zookeeper.apache.org%3E
