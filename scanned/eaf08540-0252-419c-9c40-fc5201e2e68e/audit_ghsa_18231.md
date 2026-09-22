# [H] Envoy: Race condition in Dynamic Forward Proxy leads to use-after-free and segmentation faults

## Summary
Severity: High
Advisory: GHSA-g9vw-6pvx-7gmw
CVE: CVE-2025-54588
CWE: CWE-416
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-g9vw-6pvx-7gmw
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/envoy` — affected >=1.35.0 <1.35.1
- Go: `github.com/envoyproxy/envoy` — affected >=1.34.0 <1.34.5

## Details
### Summary

A use-after-free (UAF) vulnerability in Envoy's DNS cache causes abnormal process termination. Envoy may reallocate memory when processing a pending DNS resolution, causing list iterator to reference freed memory.

### Details

The vulnerability exists in Envoy's Dynamic Forward Proxy implementation starting from version v1.34.0. The issue occurs when a completion callback for a DNS resolution triggers new DNS resolutions or removes existing pending resolutions. This condition may occur in the following configuration:

1. Dynamic Forwarding Filter is enabled.
2. `envoy.reloadable_features.dfp_cluster_resolves_hosts` runtime flag is enabled.
3. The Host header is modified between the Dynamic Forwarding Filter and Router filters.

### Impact

Denial of service due to abnormal process termination.

### Attack vector(s)
Request to Envoy configured as indicated above.

### Patches
Users should upgrade to v1.35.1 or v1.34.5. 

### Workaround
Set the `envoy.reloadable_features.dfp_cluster_resolves_hosts` runtime flag to `false`.

### Detection
Abnormal process termination with the `Envoy::Event::DispatcherImpl::runPostCallbacks()` frame in the call stack.

### Credits
Rohit Agrawal ([agrawroh](https://github.com/agrawroh)) ([rohit.agrawal@databricks.com](mailto:rohit.agrawal@databricks.com))

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-g9vw-6pvx-7gmw
- https://nvd.nist.gov/vuln/detail/CVE-2025-54588
- https://github.com/envoyproxy/envoy
- https://github.com/envoyproxy/envoy/releases/tag/v1.34.5
- https://github.com/envoyproxy/envoy/releases/tag/v1.35.1
