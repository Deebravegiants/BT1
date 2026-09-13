# [M] OAuth Identity Token exposure in Grafana

## Summary
Severity: Medium
Advisory: BIT-grafana-2022-21673
Aliases: CVE-2022-21673, GHSA-8wjh-59cw-9xh4
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-2022-21673
Type: osv

## Affected
- Bitnami: `grafana` — affected >=8.0.0 <8.3.4

## Details
Grafana is an open-source platform for monitoring and observability. In affected versions when a data source has the Forward OAuth Identity feature enabled, sending a query to that datasource with an API token (and no other user credentials) will forward the OAuth Identity of the most recently logged-in user. This can allow API token holders to retrieve data for which they may not have intended access. This attack relies on the Grafana instance having data sources that support the Forward OAuth Identity feature, the Grafana instance having a data source with the Forward OAuth Identity feature toggled on, the Grafana instance having OAuth enabled, and the Grafana instance having usable API keys. This issue has been patched in versions 7.5.13 and 8.3.4.

## References
- https://github.com/grafana/grafana/releases/tag/v7.5.13
- https://github.com/grafana/grafana/releases/tag/v8.3.4
- https://github.com/grafana/grafana/security/advisories/GHSA-8wjh-59cw-9xh4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2PFW6Q2LXXWTFRTMTRN4ZGADFRQPKJ3D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/36GUEPA5TPSC57DZTPYPBL6T7UPQ2FRH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HLAQRRGNSO5MYCPAXGPH2OCSHOGHSQMQ/
- https://security.netapp.com/advisory/ntap-20220303-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2022-21673
