# [H] Arbitrary code execution in Apache Commons BeanUtils

## Summary
Severity: High
Advisory: GHSA-p66x-2cv9-qq3v
CVE: CVE-2014-0114
CWE: CWE-20
Ecosystem: Maven
Published: 2020-06-10
Source: https://github.com/advisories/GHSA-p66x-2cv9-qq3v
Type: github-advisory

## Affected
- Maven: `commons-beanutils:commons-beanutils` — affected >=1.8.0 <1.9.4

## Details
Apache Commons BeanUtils, as distributed in lib/commons-beanutils-1.8.0.jar in Apache Struts 1.x through 1.3.10 and in other products requiring commons-beanutils through 1.9.2, does not suppress the class property, which allows remote attackers to "manipulate" the ClassLoader and execute arbitrary code via the class parameter, as demonstrated by the passing of this parameter to the getClass method of the ActionForm object in Struts 1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-0114
- https://github.com/apache/commons-beanutils/pull/7
- https://github.com/apache/commons-beanutils/commit/62e82ad92cf4818709d6044aaf257b73d42659a4
- https://lists.apache.org/thread.html/aa4ca069c7aea5b1d7329bc21576c44a39bcc4eb7bb2760c4b16f2f6%40%3Cissues.commons.apache.org%3E
- https://lists.apache.org/thread.html/aa4ca069c7aea5b1d7329bc21576c44a39bcc4eb7bb2760c4b16f2f6@%3Cissues.commons.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442%40%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/b0656d359c7d40ec9f39c8cc61bca66802ef9a2a12ee199f5b0c1442@%3Cdev.drill.apache.org%3E
- https://lists.apache.org/thread.html/c24c0b931632a397142882ba248b7bd440027960f22845c6f664c639%40%3Ccommits.commons.apache.org%3E
- https://lists.apache.org/thread.html/c24c0b931632a397142882ba248b7bd440027960f22845c6f664c639@%3Ccommits.commons.apache.org%3E
- https://lists.apache.org/thread.html/c70da3cb6e3f03e0ad8013e38b6959419d866c4a7c80fdd34b73f25c%40%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/c70da3cb6e3f03e0ad8013e38b6959419d866c4a7c80fdd34b73f25c@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/c7e31c3c90b292e0bafccc4e1b19c9afc1503a65d82cb7833dfd7478%40%3Cissues.commons.apache.org%3E
- https://lists.apache.org/thread.html/c7e31c3c90b292e0bafccc4e1b19c9afc1503a65d82cb7833dfd7478@%3Cissues.commons.apache.org%3E
- https://lists.apache.org/thread.html/cee6b1c4533be1a753614f6a7d7c533c42091e7cafd7053b8f62792a%40%3Cissues.commons.apache.org%3E
- https://lists.apache.org/thread.html/cee6b1c4533be1a753614f6a7d7c533c42091e7cafd7053b8f62792a@%3Cissues.commons.apache.org%3E
- https://lists.apache.org/thread.html/d27c51b3c933f885460aa6d3004eb228916615caaaddbb8e8bfeeb40%40%3Cgitbox.activemq.apache.org%3E
- https://lists.apache.org/thread.html/d27c51b3c933f885460aa6d3004eb228916615caaaddbb8e8bfeeb40@%3Cgitbox.activemq.apache.org%3E
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://lists.apache.org/thread.html/9b5505632f5683ee17bda4f7878525e672226c7807d57709283ffa64@%3Cissues.commons.apache.org%3E
- https://lists.apache.org/thread.html/9b5505632f5683ee17bda4f7878525e672226c7807d57709283ffa64%40%3Cissues.commons.apache.org%3E
