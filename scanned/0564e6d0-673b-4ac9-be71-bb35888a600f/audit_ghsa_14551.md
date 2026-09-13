# [H] Hippo4j privilege escalation issue

## Summary
Severity: High
Advisory: GHSA-fvx4-8h2x-gm9q
CVE: CVE-2023-27094
CWE: CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-fvx4-8h2x-gm9q
Type: github-advisory

## Affected
- Maven: `cn.hippo4j:hippo4j-all` — affected >=0

## Details
An issue found in OpenGoofy Hippo4j v.1.4.3 allows attackers to escalate privileges via the ThreadPoolController of the tenant Management module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27094
- https://github.com/opengoofy/hippo4j/issues/1059
- https://github.com/opengoofy/hippo4j
- https://github.com/opengoofy/hippo4j/blob/develop/hippo4j-server/hippo4j-console/src/main/java/cn/hippo4j/console/controller/ThreadPoolController.java
