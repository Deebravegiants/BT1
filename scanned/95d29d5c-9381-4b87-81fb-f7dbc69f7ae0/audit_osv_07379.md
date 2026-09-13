# [M] Arbitrary redirects under /new endpoint

## Summary
Severity: Medium
Advisory: BIT-prometheus-2021-29622
Aliases: CVE-2021-29622, GHSA-vx57-7f4q-fpc7
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-prometheus-2021-29622
Type: osv

## Affected
- Bitnami: `prometheus` — affected >=2.27.0 <2.27.1

## Details
Prometheus is an open-source monitoring system and time series database. In 2.23.0, Prometheus changed its default UI to the New ui. To ensure a seamless transition, the URL's prefixed by /new redirect to /. Due to a bug in the code, it is possible for an attacker to craft an URL that can redirect to any other URL, in the /new endpoint. If a user visits a prometheus server with a specially crafted address, they can be redirected to an arbitrary URL. The issue was patched in the 2.26.1 and 2.27.1 releases. In 2.28.0, the /new endpoint will be removed completely. The workaround is to disable access to /new via a reverse proxy in front of Prometheus.

## References
- https://github.com/prometheus/prometheus/releases/tag/v2.26.1
- https://github.com/prometheus/prometheus/releases/tag/v2.27.1
- https://github.com/prometheus/prometheus/security/advisories/GHSA-vx57-7f4q-fpc7
- https://nvd.nist.gov/vuln/detail/CVE-2021-29622
