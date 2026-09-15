# [M] Segmentation fault leading to crash in Envoy

## Summary
Severity: Medium
Advisory: BIT-envoy-2022-29224
Aliases: CVE-2022-29224, GHSA-m4j9-86g3-8f49
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2022-29224
Type: osv

## Affected
- Bitnami: `envoy` — affected >=0 <1.22.1

## Details
Envoy is a cloud-native high-performance proxy. Versions of envoy prior to 1.22.1 are subject to a segmentation fault in the GrpcHealthCheckerImpl. Envoy can perform various types of upstream health checking. One of them uses gRPC. Envoy also has a feature which can “hold” (prevent removal) upstream hosts obtained via service discovery until configured active health checking fails. If an attacker controls an upstream host and also controls service discovery of that host (via DNS, the EDS API, etc.), an attacker can crash Envoy by forcing removal of the host from service discovery, and then failing the gRPC health check request. This will crash Envoy via a null pointer dereference. Users are advised to upgrade to resolve this vulnerability. Users unable to upgrade may disable gRPC health checking and/or replace it with a different health checking type as a mitigation.

## References
- https://github.com/envoyproxy/envoy/commit/9b1c3962172a972bc0359398af6daa3790bb59db
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-m4j9-86g3-8f49
- https://nvd.nist.gov/vuln/detail/CVE-2022-29224
