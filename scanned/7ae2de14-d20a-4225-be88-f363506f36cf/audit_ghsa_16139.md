# [H] hornetq vulnerable to file overwrite, sensitive information disclosure

## Summary
Severity: High
Advisory: GHSA-r7mv-mv7m-pjw3
CVE: CVE-2024-51127
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-11-04
Source: https://github.com/advisories/GHSA-r7mv-mv7m-pjw3
Type: github-advisory

## Affected
- Maven: `org.hornetq:hornetq-core-client` — affected >=0

## Details
An issue in the `createTempFile` method of hornetq v2.4.9 allows attackers to arbitrarily overwrite files or access sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-51127
- https://github.com/JAckLosingHeart/CWE-378/blob/main/CVE-2024-51127.md
- https://github.com/darranl/hornetq
- https://github.com/hornetq/hornetq/blob/HornetQ_2_4_9_Final/hornetq-core-client/src/main/java/org/hornetq/core/client/impl/ClientConsumerImpl.java#L665C35-L665C49
- http://hornetq.com
