# [H] HTTP/1: sending overload crashes when the request is reset beforehand in envoy

## Summary
Severity: High
Advisory: BIT-envoy-2024-53270
Aliases: CVE-2024-53270, GHSA-q9qv-8j52-77p3
Ecosystem: Bitnami
Published: 2024-12-20
Source: https://osv.dev/vulnerability/BIT-envoy-2024-53270
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.32.0 <1.32.3

## Details
Envoy is a cloud-native high-performance edge/middle/service proxy. In affected versions `sendOverloadError` is going to assume the active request exists when `envoy.load_shed_points.http1_server_abort_dispatch` is configured. If `active_request` is nullptr, only onMessageBeginImpl() is called. However, the `onMessageBeginImpl` will directly return ok status if the stream is already reset leading to the nullptr reference. The downstream reset can actually happen during the H/2 upstream reset. As a result envoy may crash. This issue has been addressed in releases 1.32.3, 1.31.5, 1.30.9, and 1.29.12. Users are advised to upgrade. Users unable to upgrade may disable `http1_server_abort_dispatch` load shed point and/or use a high threshold.

## References
- https://github.com/envoyproxy/envoy/pull/37743/commits/6cf8afda956ba67c9afad185b962325a5242ef02
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-q9qv-8j52-77p3
- https://nvd.nist.gov/vuln/detail/CVE-2024-53270
