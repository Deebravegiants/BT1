# [C] Deserialization of Untrusted Data in Log4j

## Summary
Severity: Critical
Advisory: GHSA-2qrg-x229-3v8q
CVE: CVE-2019-17571
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-01-06
Source: https://github.com/advisories/GHSA-2qrg-x229-3v8q
Type: github-advisory

## Affected
- Maven: `log4j:log4j` — affected >=1.2
- Maven: `org.zenframework.z8.dependencies.commons:log4j-1.2.17` — affected 2.0

## Details
Included in Log4j 1.2 is a SocketServer class that is vulnerable to deserialization of untrusted data which can be exploited to remotely execute arbitrary code when combined with a deserialization gadget when listening to untrusted network traffic for log data. This affects Log4j versions 1.2 up to 1.2.17.

Users are advised to migrate to `org.apache.logging.log4j:log4j-core`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17571
- https://lists.apache.org/thread.html/ra54fa49be3e773d99ccc9c2a422311cf77e3ecd3b8594ee93043a6b1@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra9611a8431cb62369bce8909d7645597e1dd45c24b448836b1e54940%40%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/ra9611a8431cb62369bce8909d7645597e1dd45c24b448836b1e54940@%3Cissues.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/raedd12dc24412b3780432bf202a2618a21a727788543e5337a458ead%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/raedd12dc24412b3780432bf202a2618a21a727788543e5337a458ead@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb1b29aee737e1c37fe1d48528cb0febac4f5deed51f5412e6fdfe2bf%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb1b29aee737e1c37fe1d48528cb0febac4f5deed51f5412e6fdfe2bf@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb3c94619728c8f8c176d8e175e0a1086ca737ecdfcd5a2214bb768bc%40%3Ccommits.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rb3c94619728c8f8c176d8e175e0a1086ca737ecdfcd5a2214bb768bc@%3Ccommits.bookkeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbc45eb0f53fd6242af3e666c2189464f848a851d408289840cecc6e3%40%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbc45eb0f53fd6242af3e666c2189464f848a851d408289840cecc6e3@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbd19de368abf0764e4383ec44d527bc9870176f488a494f09a40500d%40%3Ccommon-dev.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/rbd19de368abf0764e4383ec44d527bc9870176f488a494f09a40500d@%3Ccommon-dev.hadoop.apache.org%3E
- https://lists.apache.org/thread.html/rbdf18e39428b5c80fc35113470198b1fe53b287a76a46b0f8780b5fd%40%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbdf18e39428b5c80fc35113470198b1fe53b287a76a46b0f8780b5fd@%3Cdev.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7%40%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7@%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7@%3Cusers.kafka.apache.org%3E
