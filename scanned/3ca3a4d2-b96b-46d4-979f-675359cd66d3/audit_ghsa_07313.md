# [M] Contour has Improper JWT Verification for Non-SNI Requests on Virtual Hosts with Fallback Certificate Enabled

## Summary
Severity: Medium
Advisory: GHSA-g3xr-5w5j-w4q4
CVE: CVE-2026-50149
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-g3xr-5w5j-w4q4
Type: github-advisory

## Affected
- Go: `github.com/projectcontour/contour` — affected >=1.23.0 <1.33.5

## Details
### Impact

When an `HTTPProxy` is configured with incompatible combination of both `.spec.virtualhost.tls.enableFallbackCertificate: true` and `.spec.virtualhost.jwtProviders`, Contour does not reject the configuration. Consequently, requests from clients that do not send TLS SNI or send an unrecognized SNI (one that does not match any `HTTPProxy` FQDN) bypass configured JWT verification and are proxied to upstream services without a valid token.

To list all `HTTPProxies` with this invalid configuration, run

```bash
kubectl get httpproxies -A -o json | jq -r '
  .items[]
  | select(.spec.virtualhost | .tls.enableFallbackCertificate and .jwtProviders)
  | "Invalid HTTPProxy found: \(.metadata.namespace)/\(.metadata.name)"
'
```

### Patches

This issue is fixed in Contour v1.33.5. Contour now rejects and marks invalid any `HTTPProxy` resources that combine `.spec.virtualhost.tls.enableFallbackCertificate: true` with `.spec.virtualhost.jwtProviders`. Affected resources will receive a status  condition with the error reason `TLSIncompatibleFeatures`.

### Workarounds

Do not enable `.spec.virtualhost.tls.enableFallbackCertificate` on `HTTPProxy` resources that also define `.spec.virtualhost.jwtProviders`. Remove one of the two settings to avoid the invalid configuration.

### References

- Contour fallback certificate documentation: https://projectcontour.io/docs/main/config/tls-termination/#fallback-certificate
- Contour JWT verification documentation: https://projectcontour.io/docs/main/config/jwt-verification/

## References
- https://github.com/projectcontour/contour/security/advisories/GHSA-g3xr-5w5j-w4q4
- https://github.com/projectcontour/contour
