# [M] Missing Authorization in Kibana Leading to Unauthorized Information Disclosure

## Summary
Severity: Medium
Advisory: BIT-kibana-2026-63143
Aliases: BIT-elk-2026-63143, CVE-2026-63143
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-kibana-2026-63143
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.4.0 <9.4.4

## Details
Missing Authorization (CWE-862) in Kibana can lead to unauthorized information disclosure via Privilege Abuse (CAPEC-122). A user with limited feature privileges can access workflow execution outputs in their Kibana space without the authorization required to do so through the documented API. The accessible data may include sensitive information returned by workflow steps, such as results from connected data sources that the caller would not otherwise be authorized to access.

## References
- https://discuss.elastic.co/t/kibana-9-3-8-9-4-4-security-update-esa-2026-67/388569
- https://nvd.nist.gov/vuln/detail/CVE-2026-63143
