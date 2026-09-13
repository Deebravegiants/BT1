# [H] BIT-grafana-2023-1387

## Summary
Severity: High
Advisory: BIT-grafana-2023-1387
Aliases: CVE-2023-1387, GHSA-5585-m9r5-p86j
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-2023-1387
Type: osv

## Affected
- Bitnami: `grafana` — affected >=9.4.0 <9.4.9

## Details
Grafana is an open-source platform for monitoring and observability. 

Starting with the 9.1 branch, Grafana introduced the ability to search for a JWT in the URL query parameter auth_token and use it as the authentication token. 

By enabling the "url_login" configuration option (disabled by default), a JWT might be sent to data sources. If an attacker has access to the data source, the leaked token could be used to authenticate to Grafana.

## References
- https://github.com/grafana/bugbounty/security/advisories/GHSA-5585-m9r5-p86j
- https://grafana.com/security/security-advisories/cve-2023-1387/
- https://security.netapp.com/advisory/ntap-20230609-0003/
- https://nvd.nist.gov/vuln/detail/CVE-2023-1387
