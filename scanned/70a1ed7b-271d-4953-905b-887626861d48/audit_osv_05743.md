# [M] SSRF in CSV Datasource Plugin

## Summary
Severity: Medium
Advisory: BIT-grafana-2023-5122
Aliases: CVE-2023-5122
Ecosystem: Bitnami
Published: 2024-10-24
Source: https://osv.dev/vulnerability/BIT-grafana-2023-5122
Type: osv

## Affected
- Bitnami: `grafana` — affected >=0 <0.6.13

## Details
Grafana is an open-source platform for monitoring and observability. The CSV datasource plugin is a Grafana Labs maintained plugin for Grafana that allows for retrieving and processing CSV data from a remote endpoint configured by an administrator. If this plugin was configured to send requests to a bare host with no path (e.g.  https://www.example.com/ https://www.example.com/` ), requests to an endpoint other than the one configured by the administrator could be triggered by a specially crafted request from any user, resulting in an SSRF vector. AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator

## References
- https://grafana.com/security/security-advisories/cve-2023-5122/
- https://security.netapp.com/advisory/ntap-20240503-0002/
- https://nvd.nist.gov/vuln/detail/CVE-2023-5122
