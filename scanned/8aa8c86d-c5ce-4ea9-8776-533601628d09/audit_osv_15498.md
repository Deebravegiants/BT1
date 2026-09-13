# [H] CVE-2019-16869

## Summary
Severity: High
Advisory: CVE-2019-16869
Aliases: GHSA-p979-4mfw-53vg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-09-26
Source: https://osv.dev/vulnerability/CVE-2019-16869
Type: osv

## Details
Netty before 4.1.42.Final mishandles whitespace before the colon in HTTP headers (such as a "Transfer-Encoding : chunked" line), which leads to HTTP request smuggling.

## References
- https://github.com/poc-effectiveness/PoCAdaptation/tree/main/Adapted/CVE-2019-16869/5.0.0.Alpha1/exploit
- https://lists.apache.org/thread.html/0acadfb96176768caac79b404110df62d14d30aa9d53b6dbdb1407ac%40%3Cissues.spark.apache.org%3E
- https://lists.apache.org/thread.html/0acadfb96176768caac79b404110df62d14d30aa9d53b6dbdb1407ac@%3Cissues.spark.apache.org%3E
- https://lists.apache.org/thread.html/19fed892608db1efe5a5ce14372137669ff639df0205323959af7de3%40%3Cdev.olingo.apache.org%3E
- https://lists.apache.org/thread.html/19fed892608db1efe5a5ce14372137669ff639df0205323959af7de3@%3Cdev.olingo.apache.org%3E
- https://lists.apache.org/thread.html/2494a2ac7f66af6e4646a4937b17972a4ec7cd3c7333c66ffd6c639d%40%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/2494a2ac7f66af6e4646a4937b17972a4ec7cd3c7333c66ffd6c639d@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/2e1cf538b502713c2c42ffa46d81f4688edb5676eb55bd9fc4b4fed7%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/2e1cf538b502713c2c42ffa46d81f4688edb5676eb55bd9fc4b4fed7@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/35961d1ae00849974353a932b4fef12ebce074541552eceefa04f1fd%40%3Cdev.olingo.apache.org%3E
- https://lists.apache.org/thread.html/35961d1ae00849974353a932b4fef12ebce074541552eceefa04f1fd@%3Cdev.olingo.apache.org%3E
- https://lists.apache.org/thread.html/37ed432b8eb35d8bd757f53783ec3e334bd51f514534432bea7f1c3d%40%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/37ed432b8eb35d8bd757f53783ec3e334bd51f514534432bea7f1c3d@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/380f6d2730603a2cd6b0a8bea9bcb21a86c199147e77e448c5f7390b%40%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/380f6d2730603a2cd6b0a8bea9bcb21a86c199147e77e448c5f7390b@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/3e6d7aae1cca10257e3caf2d69b22f74c875f12a1314155af422569d%40%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/3e6d7aae1cca10257e3caf2d69b22f74c875f12a1314155af422569d@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/51923a9ba513b2e816e02a9d1fd8aa6f12e3e4e99bbd9dc884bccbbe%40%3Cissues.spark.apache.org%3E
- https://lists.apache.org/thread.html/51923a9ba513b2e816e02a9d1fd8aa6f12e3e4e99bbd9dc884bccbbe@%3Cissues.spark.apache.org%3E
- https://lists.apache.org/thread.html/519eb0fd45642dcecd9ff74cb3e71c20a4753f7d82e2f07864b5108f%40%3Cdev.drill.apache.org%3E
