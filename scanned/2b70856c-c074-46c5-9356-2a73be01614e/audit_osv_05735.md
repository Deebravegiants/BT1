# [C] BIT-grafana-2022-28660

## Summary
Severity: Critical
Advisory: BIT-grafana-2022-28660
Aliases: CVE-2022-28660
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-2022-28660
Type: osv

## Affected
- Bitnami: `grafana` — affected >=1.1.0 <1.2.1, >=1.3.0

## Details
The querier component in Grafana Enterprise Logs 1.1.x through 1.3.x before 1.4.0 does not require authentication when X-Scope-OrgID is used. Versions 1.2.1, 1.3.1, and 1.4.0 contain the bugfix. This affects -auth.type=enterprise in microservices mode

## References
- https://grafana.com/docs/enterprise-logs/latest/gel-releases/#v121----may-3-2022
- https://security.netapp.com/advisory/ntap-20220707-0004/
