# [M] Apache Superset: Allows for uncontrolled resource consumption via a ZIP bomb (version range fix for CVE-2023-46104)

## Summary
Severity: Medium
Advisory: BIT-superset-2024-23952
Aliases: CVE-2024-23952
Ecosystem: Bitnami
Published: 2025-02-05
Source: https://osv.dev/vulnerability/BIT-superset-2024-23952
Type: osv

## Affected
- Bitnami: `superset` — affected >=0 <4.1.1

## Details
This is a duplicate for CVE-2023-46104. With correct CVE version ranges for affected Apache Superset.
 
Uncontrolled resource consumption can be triggered by authenticated attacker that uploads a malicious ZIP to import database, dashboards or datasets.  
This vulnerability exists in Apache Superset versions up to and including 2.1.2 and versions 3.0.0, 3.0.1.

## References
- http://www.openwall.com/lists/oss-security/2024/02/14/2
- http://www.openwall.com/lists/oss-security/2024/02/14/3
- https://lists.apache.org/thread/zc58zvm4414molqn2m4d4vkrbrsxdksx
- https://nvd.nist.gov/vuln/detail/CVE-2024-23952
