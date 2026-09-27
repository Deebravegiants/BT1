# [M] BIT-elk-2020-7016

## Summary
Severity: Medium
Advisory: BIT-elk-2020-7016
Aliases: BIT-kibana-2020-7016, CVE-2020-7016
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-elk-2020-7016
Type: osv

## Affected
- Bitnami: `elk` — affected >=7.0.0 <7.8.1

## Details
Kibana versions before 6.8.11 and 7.8.1 contain a denial of service (DoS) flaw in Timelion. An attacker can construct a URL that when viewed by a Kibana user can lead to the Kibana process consuming large amounts of CPU and becoming unresponsive.

## References
- https://discuss.elastic.co/t/elastic-stack-6-8-11-and-7-8-1-security-update/242786
- https://www.elastic.co/community/security/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://nvd.nist.gov/vuln/detail/CVE-2020-7016
