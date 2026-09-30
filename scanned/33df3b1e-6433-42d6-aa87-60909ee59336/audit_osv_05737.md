# [H] BIT-grafana-2022-32275

## Summary
Severity: High
Advisory: BIT-grafana-2022-32275
Aliases: CVE-2022-32275
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-2022-32275
Type: osv

## Affected
- Bitnami: `grafana` — affected >=8.4.3 <8.4.4

## Details
Grafana 8.4.3 allows reading files via (for example) a /dashboard/snapshot/%7B%7Bconstructor.constructor'/.. /.. /.. /.. /.. /.. /.. /.. /etc/passwd URI. NOTE: the vendor's position is that there is no vulnerability; this request yields a benign error page, not /etc/passwd content

## References
- https://github.com/BrotherOfJhonny/grafana
- https://github.com/BrotherOfJhonny/grafana/blob/main/README.md
- https://github.com/grafana/grafana/issues/50336
- https://github.com/grafana/grafana/issues/50341#issuecomment-1155252393
- https://grafana.com
- https://security.netapp.com/advisory/ntap-20220715-0008/
- https://nvd.nist.gov/vuln/detail/CVE-2022-32275
