# [H] Grafana Image Renderer leaking files

## Summary
Severity: High
Advisory: BIT-grafana-image-renderer-2022-31176
Aliases: CVE-2022-31176, GHSA-2cfh-233g-m4c5
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-image-renderer-2022-31176
Type: osv

## Affected
- Bitnami: `grafana-image-renderer` — affected >=0 <3.6.1

## Details
Grafana Image Renderer is a Grafana backend plugin that handles rendering of panels & dashboards to PNGs using a headless browser (Chromium/Chrome). An internal security review identified an unauthorized file disclosure vulnerability. It is possible for a malicious user to retrieve unauthorized files under some network conditions or via a fake datasource (if user has admin permissions in Grafana). All Grafana installations should be upgraded to version 3.6.1 as soon as possible. As a workaround it is possible to [disable HTTP remote rendering](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#plugingrafana-image-renderer).

## References
- https://github.com/grafana/grafana-image-renderer/pull/364
- https://github.com/grafana/grafana-image-renderer/security/advisories/GHSA-2cfh-233g-m4c5
- https://security.netapp.com/advisory/ntap-20221209-0004/
- https://nvd.nist.gov/vuln/detail/CVE-2022-31176
