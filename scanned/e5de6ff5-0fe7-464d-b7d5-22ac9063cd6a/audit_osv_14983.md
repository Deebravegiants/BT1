# [M] CVE-2019-12814

## Summary
Severity: Medium
Advisory: CVE-2019-12814
Aliases: GHSA-cmfg-87vq-g5g4
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-12814
Type: osv

## Details
A Polymorphic Typing issue was discovered in FasterXML jackson-databind 2.x through 2.9.9. When Default Typing is enabled (either globally or for a specific property) for an externally exposed JSON endpoint and the service has JDOM 1.x or 2.x jar in the classpath, an attacker can send a specifically crafted JSON message that allows them to read arbitrary local files on the server.

## References
- https://lists.apache.org/thread.html/0d4b630d9ee724aee50703397d9d1afa2b2befc9395ba7797d0ccea9%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/129da0204c876f746636018751a086cc581e0e07bcdeb3ee22ff5731%40%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/15a55e1d837fa686db493137cc0330c7ee1089ed9a9eea7ae7151ef1%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/1e04d9381c801b31ab28dec813c31c304b2a596b2a3707fa5462c5c0%40%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/28be28ffd6471d230943a255c36fe196a54ef5afc494a4781d16e37c%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/2d2a76440becb610b9a9cb49b15eac3934b02c2dbcaacde1000353e4%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/2ff264b6a94c5363a35c4c88fa93216f60ec54d1d973ed6b76a9f560%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/34717424b4d08b74f65c09a083d6dd1cb0763f37a15d6de135998c1d%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/3f99ae8dcdbd69438cb733d745ee3ad5e852068490719a66509b4592%40%3Ccommits.cassandra.apache.org%3E
- https://lists.apache.org/thread.html/4b832d1327703d6b287a6d223307f8f884d798821209a10647e93324%40%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f%40%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/56c8042873595b8c863054c7bfccab4bf2c01c6f5abedae249d914b9%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/5ecc333113b139429f4f05000d4aa2886974d4df3269c1dd990bb319%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/5fc0e16b7af2590bf1e97c76c136291c4fdb244ee63c65c485c9a7a1%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/71f9ffd92410a889e27b95a219eaa843fd820f8550898633d85d4ea3%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/87e46591de8925f719664a845572d184027258c5a7af0a471b53c77b%40%3Cdev.tomee.apache.org%3E
- https://lists.apache.org/thread.html/8fe2983f6d9fee0aa737e4bd24483f8f5cf9b938b9adad0c4e79b2a4%40%3Cnotifications.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/940b4c3fef002461b89a050935337056d4a036a65ef68e0bbd4621ef%40%3Cdev.struts.apache.org%3E
- https://lists.apache.org/thread.html/a3ae8a8c5e32c413cd27071d3a204166050bf79ce7f1299f6866338f%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/a62aa2706105d68f1c02023fe24aaa3c13b4d8a1826181fed07d9682%40%3Cnotifications.zookeeper.apache.org%3E
