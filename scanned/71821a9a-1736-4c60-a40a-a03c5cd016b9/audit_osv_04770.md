# [C] Envoy client may fake the header `x-envoy-original-path`

## Summary
Severity: Critical
Advisory: BIT-envoy-2023-27487
Aliases: CVE-2023-27487, GHSA-5375-pq35-hf2g
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-envoy-2023-27487
Type: osv

## Affected
- Bitnami: `envoy` — affected >=1.25.0 <1.25.3

## Details
Envoy is an open source edge and service proxy designed for cloud-native applications. Prior to versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9, the client may bypass JSON Web Token (JWT) checks and forge fake original paths. The header `x-envoy-original-path` should be an internal header, but Envoy does not remove this header from the request at the beginning of request processing when it is sent from an untrusted client. The faked header would then be used for trace logs and grpc logs, as well as used in the URL used for `jwt_authn` checks if the `jwt_authn` filter is used, and any other upstream use of the x-envoy-original-path header. Attackers may forge a trusted `x-envoy-original-path` header. Versions 1.26.0, 1.25.3, 1.24.4, 1.23.6, and 1.22.9 have patches for this issue.

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-5375-pq35-hf2g
- https://nvd.nist.gov/vuln/detail/CVE-2023-27487
