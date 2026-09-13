# [H] Grafana Enterprise datasource network restrictions bypass via HTTP redirects

## Summary
Severity: High
Advisory: BIT-grafana-2022-29170
Aliases: CVE-2022-29170, GHSA-9rrr-6fq2-4f99
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-2022-29170
Type: osv

## Affected
- Bitnami: `grafana` — affected >=8.0.0 <8.5.3

## Details
Grafana is an open-source platform for monitoring and observability. In Grafana Enterprise, the Request security feature allows list allows to configure Grafana in a way so that the instance doesn’t call or only calls specific hosts. The vulnerability present starting with version 7.4.0 and prior to versions 7.5.16 and 8.5.3 allows someone to bypass these security configurations if a malicious datasource (running on an allowed host) returns an HTTP redirect to a forbidden host. The vulnerability only impacts Grafana Enterprise when the Request security allow list is used and there is a possibility to add a custom datasource to Grafana which returns HTTP redirects. In this scenario, Grafana would blindly follow the redirects and potentially give secure information to the clients. Grafana Cloud is not impacted by this vulnerability. Versions 7.5.16 and 8.5.3 contain a patch for this issue. There are currently no known workarounds.

## References
- https://github.com/grafana/grafana/pull/49240
- https://github.com/grafana/grafana/releases/tag/v7.5.16
- https://github.com/grafana/grafana/releases/tag/v8.5.3
- https://github.com/grafana/grafana/security/advisories/GHSA-9rrr-6fq2-4f99
- https://security.netapp.com/advisory/ntap-20220707-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2022-29170
