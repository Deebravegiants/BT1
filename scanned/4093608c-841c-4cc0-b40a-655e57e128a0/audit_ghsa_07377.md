# [H] Envoy Gateway: xDS Control Plane Information Disclosure when operating in GatewayNamespaceMode 

## Summary
Severity: High
Advisory: GHSA-22xc-xg2r-9j7v
CVE: CVE-2026-53714
CWE: CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-22xc-xg2r-9j7v
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/gateway` — affected >=1.8.0-rc.0 <1.8.1
- Go: `github.com/envoyproxy/gateway` — affected >=0 <1.7.4

## Details
### Impact
When Envoy Gateway runs in GatewayNamespaceMode (`provider.kubernetes.deploy.type=GatewayNamespace`), the xDS gRPC server is configured with a `StreamInterceptor` for JWT authentication but no UnaryInterceptor. The go-control-plane xDS server exposes both streaming and unary (Fetch) RPC methods for all registered discovery services. Since there is no unary interceptor, these Fetch endpoints are completely unauthenticated. 

Additionally, the JWT authentication interceptor in GatewayNamespaceMode only validates tokens when the received gRPC message is of type `discoveryv3.DeltaDiscoveryRequest` . If the message is a `discoveryv3.DiscoveryRequest` — used by the State-of-the-World (SotW) xDS protocol — the type assertion fails, the validation block is skipped entirely, and RecvMsg returns nil (success) without any authentication.

Any pod in the cluster that can reach the xDS server (port 18000) can use the SotW protocol to bypass JWT authentication and access:

* TLS private keys via StreamSecrets (SDS)
* All xDS resources via StreamAggregatedResources (ADS)
* Backend endpoints via StreamClusters / StreamEndpoints (CDS/EDS)
* Routing rules via StreamRoutes / StreamListeners (RDS/LDS)

### Credits

Envoy Gateway thanks @dashingDragon and @Donjon-Cerberus for reporting this issue.

## References
- https://github.com/envoyproxy/gateway/security/advisories/GHSA-22xc-xg2r-9j7v
- https://github.com/envoyproxy/gateway
