# [M] Istio: SSRF via RequestAuthentication jwksUri

## Summary
Severity: Medium
Advisory: GHSA-fgw5-hp8f-xfhc
CVE: CVE-2026-41413
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-fgw5-hp8f-xfhc
Type: github-advisory

## Affected
- Go: `istio.io/istio` — affected >=0 <0.0.0-20260410004459-189832a289c1

## Details
### Impact

When a RequestAuthentication resource is created with a jwksUri pointing to an internal service, istiod makes an unauthenticated HTTP GET request to that URL without filtering out localhost or link local ips. This can result in sensitive data being distributed to Envoy proxies via xDS configuration.

Note: a partial mitigation for this was released in 1.29.1, 128.5, and 1.27.8; however, it was incomplete and missed a few codepaths. 1.29.2 and 1.28.6 contain the more robust fix.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

### Workarounds

Users can deploy a `ValidatingAdmissionPolicy` to prevent the creation of `RequestAuthentication` resources with suspicious jwksUri field values (e.g. localhost, 127.0.0.0/8, 169.254.0.0/16, the ipv6 variants, etc.).

### References
None

## References
- https://github.com/istio/istio/security/advisories/GHSA-fgw5-hp8f-xfhc
- https://nvd.nist.gov/vuln/detail/CVE-2026-41413
- https://github.com/istio/istio
- https://github.com/istio/istio/releases/tag/1.28.6
- https://github.com/istio/istio/releases/tag/1.29.2
