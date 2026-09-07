# [H] XML External Entity (XXE) Injection in Jackson Databind

## Summary
Severity: High
Advisory: GHSA-288c-cq4h-88gq
CVE: CVE-2020-25649
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-02-18
Source: https://github.com/advisories/GHSA-288c-cq4h-88gq
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.6.0 <2.6.7.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.7.0.0 <2.9.10.7
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.10.0.0 <2.10.5.1

## Details
A flaw was found in FasterXML Jackson Databind, where it did not have entity expansion secured properly. This flaw allows vulnerability to XML external entity (XXE) attacks. The highest threat from this vulnerability is data integrity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25649
- https://github.com/FasterXML/jackson-databind/issues/2589
- https://github.com/FasterXML/jackson-databind/commit/3d932709abd0b5390efe67451653fc9efa9db677
- https://github.com/FasterXML/jackson-databind/commit/612f971b78c60202e9cd75a299050c8f2d724a59
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://lists.apache.org/thread.html/rc82ff47853289e9cd17f5cfbb053c04cafc75ee32e3d7223963f83bb@%3Cdev.knox.apache.org%3E
- https://lists.apache.org/thread.html/rc15e90bbef196a5c6c01659e015249d6c9a73581ca9afb8aeecf00d2@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7@%3Cusers.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rbf4ce74b0d1fa9810dec50ba3ace0caeea677af7c27a97111c06ccb7@%3Cdev.kafka.apache.org%3E
- https://lists.apache.org/thread.html/rb674520b9f6c808c1bf263b1369e14048ec3243615f35cfd24e33604@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/raf13235de6df1d47a717199e1ecd700dff3236632f5c9a1488d9845b@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/ra95faf968f3463acb3f31a6fbec31453fc5045325f99f396961886d3@%3Cissues.flink.apache.org%3E
- https://lists.apache.org/thread.html/ra409f798a1e5a6652b7097429b388650ccd65fd958cee0b6f69bba00@%3Cissues.hive.apache.org%3E
- https://lists.apache.org/thread.html/ra1157e57a01d25e36b0dc17959ace758fc21ba36746de29ba1d8b130@%3Cjira.kafka.apache.org%3E
- https://lists.apache.org/thread.html/r98bfe3b90ea9408f12c4b447edcb5638703d80bc782430aa0c210a54@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r95a297eb5fd1f2d3a2281f15340e2413f952e9d5503296c3adc7201a@%3Ccommits.tomee.apache.org%3E
- https://lists.apache.org/thread.html/r94c7e86e546120f157264ba5ba61fd29b3a8d530ed325a9b4fa334d7@%3Ccommits.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r91722ecfba688b0c565675f8bf380269fde8ec62b54d6161db544c22@%3Ccommits.karaf.apache.org%3E
- https://lists.apache.org/thread.html/r90d1e97b0a743cf697d89a792a9b669909cc5a1692d1e0083a22e66c@%3Cissues.zookeeper.apache.org%3E
- https://lists.apache.org/thread.html/r900d4408c4189b376d1ec580ea7740ea6f8710dc2f0b7e9c9eeb5ae0@%3Cdev.zookeeper.apache.org%3E
