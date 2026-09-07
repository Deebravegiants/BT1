# [M] Apache Tomcat allows remote attackers to bypass intended access restrictions

## Summary
Severity: Medium
Advisory: GHSA-mg4v-rf8p-ghqq
CVE: CVE-2011-1088
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mg4v-rf8p-ghqq
Type: github-advisory

## Affected
- Maven: `org.apache.tomcat:tomcat` — affected >=7.0.0 <7.0.10

## Details
Apache Tomcat 7.x before 7.0.10 does not follow ServletSecurity annotations, which allows remote attackers to bypass intended access restrictions via HTTP requests to a web application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-1088
- https://github.com/apache/tomcat/commit/f528992ec6cd7b62c9ced5b3a7dc4cda6bfd1a5e
- https://github.com/apache/tomcat/commit/ee627412570268df47a075f5d4dc5f7debf39fad
- https://github.com/apache/tomcat/commit/ece65c1a428094b1c6c17de3d7593f64e1bb1286
- https://github.com/apache/tomcat/commit/dd10265436ea8b2fe35f1a8b09bc7390acbea269
- https://github.com/apache/tomcat/commit/dbac5e24759954daed3c584abb5d466fcf42dd4b
- https://github.com/apache/tomcat/commit/b1d1047a4c0a7754cabf57ac0303f92e4e77ef58
- https://github.com/apache/tomcat/commit/9c90bdc1ad942374b1bb6b147613497970b3c8e1
- https://github.com/apache/tomcat/commit/880b1a4fc424625b56c8bcd9ebf6bfe966a1dadd
- https://github.com/apache/tomcat/commit/63fd724e129b647b7d9026ae29513dd6b774b4b5
- https://github.com/apache/tomcat/commit/5c8560f3054982abaa476d87ec031c439d58d66e
- https://github.com/apache/tomcat/commit/3e5b0455483eed55752047073e92403bfca8d3ec
- https://github.com/apache/tomcat/commit/3ac2b5c1611af51ee5438fd32a3254a2de1878ce
- https://github.com/apache/tomcat/commit/2d7dbfe4c63a4242a9b28fdb662d91ceb7a84630
- https://github.com/apache/tomcat/commit/1b2d5e90d271ab087a36b556eb17519454170529
- https://github.com/apache/tomcat/commit/149af600532df6a24b1f7fc93607d764dfc9a7ea
- https://github.com/apache/tomcat/commit/13fe121edb6f2b597d2b82725f1b01296ac78ebd
- https://github.com/apache/tomcat/commit/0ff4905158b77787a7f3aca55c9dec93456665dc
- https://github.com/apache/tomcat/commit/0f95cb7401acdbfc9b65c878948b84bb496f2386
- https://github.com/apache/tomcat/commit/0a5a19f0c3b8d199b7335da5f88e956f59926673
