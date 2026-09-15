# [C] Kafbat UI vulnerable to Remote Code Execution by JMX in Metrices Configuration

## Summary
Severity: Critical
Advisory: CVE-2025-49127
Aliases: GHSA-g3mf-c374-fgh2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-06-06
Source: https://osv.dev/vulnerability/CVE-2025-49127
Type: osv

## Details
Kafbat UI is a web user interface for managing Apache Kafka clusters. An unsafe deserialization vulnerability in version 1.0.0 allows any unauthenticated user to execute arbitrary code on the server. Version 1.1.0 fixes the issue.

## References
- https://github.com/kafbat/kafka-ui/releases/tag/v1.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49127.json
- https://github.com/kafbat/kafka-ui/security/advisories/GHSA-g3mf-c374-fgh2
- https://nvd.nist.gov/vuln/detail/CVE-2025-49127
