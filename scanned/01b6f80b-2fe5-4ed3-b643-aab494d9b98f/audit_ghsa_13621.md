# [H] github.com/kumahq/kuma affected by CVE-2023-44487

## Summary
Severity: High
Advisory: GHSA-9wmc-rg4h-28wv
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-9wmc-rg4h-28wv
Type: github-advisory

## Affected
- Go: `github.com/kumahq/kuma` — affected >=2.4.0 <2.4.3
- Go: `github.com/kumahq/kuma` — affected >=2.3.0 <2.3.3
- Go: `github.com/kumahq/kuma` — affected >=2.2.0 <2.2.4
- Go: `github.com/kumahq/kuma` — affected >=2.1.0 <2.1.8
- Go: `github.com/kumahq/kuma` — affected >=0 <2.0.8

## Details
### Impact
Envoy and Go HTTP/2 protocol stack is vulnerable to the "Rapid Reset" class of exploits, which send a sequence of HEADERS frames optionally followed by RST_STREAM frames.

This can be exercised if you use the builtin gateway and receive untrusted http2 traffic.

### Patches

https://github.com/kumahq/kuma/pull/8023
https://github.com/kumahq/kuma/pull/8001
https://github.com/kumahq/kuma/pull/8034

### Workarounds
Disable http2 on the gateway listener with a MeshProxyPatch or ProxyTemplate.

### References
https://github.com/advisories/GHSA-qppj-fm5r-hxr3
https://github.com/golang/go/issues/63417
https://github.com/envoyproxy/envoy/security/advisories/GHSA-jhv4-f7mr-xx76
https://cloud.google.com/blog/products/identity-security/how-it-works-the-novel-http2-rapid-reset-ddos-attack
https://www.nginx.com/blog/http-2-rapid-reset-attack-impacting-f5-nginx-products/?sf269548684=1
https://www.envoyproxy.io/docs/envoy/latest/configuration/best_practices/edge

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-jhv4-f7mr-xx76
- https://github.com/kumahq/kuma/security/advisories/GHSA-9wmc-rg4h-28wv
- https://github.com/golang/go/issues/63417
- https://github.com/kumahq/kuma/pull/8001
- https://github.com/kumahq/kuma/pull/8023
- https://github.com/kumahq/kuma/pull/8034
- https://cloud.google.com/blog/products/identity-security/how-it-works-the-novel-http2-rapid-reset-ddos-attack
- https://github.com/advisories/GHSA-qppj-fm5r-hxr3
- https://github.com/kumahq/kuma
- https://www.envoyproxy.io/docs/envoy/latest/configuration/best_practices/edge
- https://www.nginx.com/blog/http-2-rapid-reset-attack-impacting-f5-nginx-products/?sf269548684=1
