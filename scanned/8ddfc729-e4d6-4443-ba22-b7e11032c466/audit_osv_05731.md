# [H] When query caching is enabled in Grafana users can query another users session

## Summary
Severity: High
Advisory: BIT-grafana-2022-23498
Aliases: CVE-2022-23498, GHSA-2j8f-6whh-frc8
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-2022-23498
Type: osv

## Affected
- Bitnami: `grafana` — affected >=9.3.0 <9.3.4

## Details
Grafana is an open-source platform for monitoring and observability. When datasource query caching is enabled, Grafana caches all headers, including `grafana_session`. As a result, any user that queries a datasource where the caching is enabled can acquire another user’s session. To mitigate the vulnerability you can disable datasource query caching for all datasources. This issue has been patched in versions 9.2.10 and 9.3.4.

## References
- https://github.com/grafana/grafana/security/advisories/GHSA-2j8f-6whh-frc8
- https://security.netapp.com/advisory/ntap-20230309-0007/
- https://nvd.nist.gov/vuln/detail/CVE-2022-23498
