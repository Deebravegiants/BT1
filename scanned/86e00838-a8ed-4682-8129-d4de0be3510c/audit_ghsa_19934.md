# [M] kube-httpcache is vulnerable to Cross-Site Request Forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-47xh-qxqv-mgvg
CWE: CWE-352
Ecosystem: Go
Published: 2022-12-02
Source: https://github.com/advisories/GHSA-47xh-qxqv-mgvg
Type: github-advisory

## Affected
- Go: `github.com/mittwald/kube-httpcache` — affected >=0 <0.7.1

## Details
### Impact

> A request forgery attack can be performed on Varnish Cache servers that have the HTTP/2 protocol turned on. An attacker may introduce characters through the HTTP/2 pseudo-headers that are invalid in the context of an HTTP/1 request line, causing the Varnish server to produce invalid HTTP/1 requests to the backend. This may in turn be used to successfully exploit vulnerabilities in a server behind the Varnish server.
> -- https://varnish-cache.org/security/VSV00011.html#vsv00011

### Patches

This is fixed in Varnish 6.0.11; Varnish 6.0.11 is available in `kube-httpcache` versions v0.7.1 and later.

### Workarounds

See [upstream mitigation hints](https://varnish-cache.org/security/VSV00011.html#mitigation).

### References

- https://varnish-cache.org/security/VSV00011.html#vsv00011

## References
- https://github.com/mittwald/kube-httpcache/security/advisories/GHSA-47xh-qxqv-mgvg
- https://github.com/mittwald/kube-httpcache
- https://varnish-cache.org/security/VSV00011.html#vsv00011
