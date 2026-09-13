# [H] Incorrect handling of internal redirects results in crash in Envoy

## Summary
Severity: High
Advisory: BIT-envoy-2022-21655
Aliases: CVE-2022-21655, GHSA-7r5p-7fmh-jxpg
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2022-21655
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.21.0 <1.21.1

## Details
Envoy is an open source edge and service proxy, designed for cloud-native applications. The envoy common router will segfault if an internal redirect selects a route configured with direct response or redirect actions. This will result in a denial of service. As a workaround turn off internal redirects if direct response entries are configured on the same listener.

## References
- https://github.com/envoyproxy/envoy/commit/177d608155ba8b11598b9bbf8240e90d8c350682
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-7r5p-7fmh-jxpg
- https://nvd.nist.gov/vuln/detail/CVE-2022-21655
