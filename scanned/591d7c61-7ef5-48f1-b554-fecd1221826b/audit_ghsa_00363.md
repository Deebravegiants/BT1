# [C] Apache Camel's Jackson and JacksonXML unmarshalling operation are vulnerable to Remote Code Execution attacks

## Summary
Severity: Critical
Advisory: GHSA-vvjc-q5vr-52q6
CVE: CVE-2016-8749
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-vvjc-q5vr-52q6
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-jackson` — affected >=0 <2.16.5
- Maven: `org.apache.camel:camel-jackson` — affected >=2.17.0 <2.17.5
- Maven: `org.apache.camel:camel-jackson` — affected >=2.18.0 <2.18.2

## Details
Apache Camel's camel-jackson and camel-jacksonxml components are vulnerable to Java object
de-serialisation vulnerability. Camel allows to specify such a type through the 'CamelJacksonUnmarshalType'
property. De-serializing untrusted data can lead to security flaws as demonstrated in various similar reports about Java de-serialization issues.

Mitigation: 2.16.x users should upgrade to 2.16.5, 2.17.x users should upgrade to 2.17.5, 2.18.x users should
upgrade to 2.18.2. 

The JIRA tickets: https://issues.apache.org/jira/browse/CAMEL-10567 and https://issues.apache.org/jira/browse/CAMEL-10604
refers to the various commits that resovoled the issue, and have more details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-8749
- https://github.com/apache/camel/commit/10f552643d7e4565104d142bbc160db5a30f9f7e
- https://github.com/apache/camel/commit/235036d2396ae45b6809b72a1983dee33b5ba326
- https://github.com/apache/camel/commit/2b0e96117d6f01eba0c18e2ff8df6a438e819721
- https://github.com/apache/camel/commit/57d01e2fc8923263df896e9810329ee5b7f9b69e
- https://github.com/apache/camel/commit/5ae9c0dcc4843347cd01ffb58ce5dd0687755a14
- https://github.com/apache/camel/commit/7567488f844f01d72840f7ab6ca18114a11f20d8
- https://github.com/apache/camel/commit/83fef7108456eeac1506853d194cd1360851c4fe
- https://github.com/apache/camel/commit/881e5099f94316d4a66ffbff0a3e6915829d49d7
- https://github.com/apache/camel/commit/8c862aa11e31d0f804c4a4516a0715e05e3eebcf
- https://github.com/apache/camel/commit/abb45b2c2ada2bbb34138230540b37d259c1e98d
- https://github.com/apache/camel/commit/ccf149c76bf37adc5977dc626e141a14e60b5aee
- https://github.com/apache/camel/commit/d4102512147eca2af21c3b6ed63a67d852f4e66a
- https://issues.apache.org/jira/browse/CAMEL-10604
- https://lists.apache.org/thread.html/2318d7f7d87724d8716cd650c21b31cb06e4d34f6d0f5ee42f28fdaf@%3Ccommits.camel.apache.org%3E
- https://lists.apache.org/thread.html/b4014ea7c5830ca1fc28edd5cafedfe93ad4af2d9e69c961c5def31d@%3Ccommits.camel.apache.org%3E
- https://www.github.com/mbechler/marshalsec/blob/master/marshalsec.pdf?raw=true
- https://issues.apache.org/jira/browse/CAMEL-10567
- https://github.com/apache/camel
- https://github.com/advisories/GHSA-vvjc-q5vr-52q6
