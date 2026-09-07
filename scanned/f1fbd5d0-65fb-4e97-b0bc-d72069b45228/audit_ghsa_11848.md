# [M] Envoy's global rate limit may crash when the response phase limit is enabled and the response phase request is failed directly

## Summary
Severity: Medium
Advisory: GHSA-c23c-rp3m-vpg3
CVE: CVE-2026-26330
CWE: CWE-416
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-c23c-rp3m-vpg3
Type: github-advisory

## Affected
- Go: `github.com/envoyproxy/envoy` — affected 1.37.0
- Go: `github.com/envoyproxy/envoy` — affected >=1.36.0

## Details
### Summary

At the rate limit filter, if we enabled the response phase limit with `apply_on_stream_done` in the rate limit configuration and the response phase limit request fails directly, it may crash Envoy.

### Details

When both the request phase limit and response phase limit are enabled, the safe gRPC client instance will be re-used for both the request phase request and response phase request.

But after the request phase request is done, the inner state of the request phase limit request in gRPC client is not cleaned up. When we send the second limit request at response phase, and the second limit request fails directly, we may access the previous request's inner state and result in crash.


### PoC

This need to mock the network failure. But we have reproduced by unit test locally.

### Impact

This only happens when both the request phase limit and response phase limit are enabled in the rate limit filter, and requires the request to rate limit service fails directly (For example, if from Envoy's perspective, no healthy endpoint for rate limit service may result the request fails directly). That's say, not easy to trigger this.

### To workaround

This could be worked around by splitting the rate limit filter. That is, if there is a rate limit filter that contains normal rate limit configuration (request phase limit, without `apply_on_stream_done`) and also rate limit configuration with `apply_on_stream_done` (response phase limit). Splitting them into two rate limit filters and ensure one filter only contains normal rate limit configuration (without `apply_on_stream_done`), and one only contains rate limit configuration with `apply_on_stream_done` could avoid this problem. 

### Credit

Mandar Jog (mandarjog@gmail.com)

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-c23c-rp3m-vpg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-26330
- https://github.com/envoyproxy/envoy
