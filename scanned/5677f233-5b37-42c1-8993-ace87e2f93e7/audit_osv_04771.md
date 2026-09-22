# [C] Envoy gRPC client produces invalid protobuf when an HTTP header with non-UTF8 value is received.

## Summary
Severity: Critical
Advisory: BIT-envoy-2023-27488
Aliases: CVE-2023-27488, GHSA-9g5w-hqr3-w2ph
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-27488
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.25.0 <1.25.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9, escalation of privileges is possible when `failure_mode_allow: true` is configured for `ext_authz` filter. For affected components that are used for logging and/or visibility, requests may not be logged by the receiving service.

When Envoy was configured to use ext_authz, ext_proc, tap, ratelimit filters, and grpc access log service and an http header with non-UTF-8 data was received, Envoy would generate an invalid protobuf message and send it to the configured service. The receiving service would typically generate an error when decoding the protobuf message. For ext_authz that was configured with ``failure_mode_allow: true``, the request would have been allowed in this case. For the other services, this could have resulted in other unforeseen errors such as a lack of visibility into requests. 

As of versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9, Envoy by default sanitizes the values sent in gRPC service calls to be valid UTF-8, replacing data that is not valid UTF-8 with a `!` character. This behavioral change can be temporarily reverted by setting runtime guard `envoy.reloadable_features.service_sanitize_non_utf8_strings` to false. As a workaround, one may set `failure_mode_allow: false` for `ext_authz`.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-9g5w-hqr3-w2ph
- https://nvd.nist.gov/vuln/detail/CVE-2023-27488
