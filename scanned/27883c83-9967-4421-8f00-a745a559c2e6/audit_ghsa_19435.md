# [M] Go-Guerrilla SMTP Daemon allows the PROXY command to be sent multiple times

## Summary
Severity: Medium
Advisory: GHSA-c2c3-pqw5-5p7c
CVE: CVE-2025-31135
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-04-01
Source: https://github.com/advisories/GHSA-c2c3-pqw5-5p7c
Type: github-advisory

## Affected
- Go: `github.com/phires/go-guerrilla` — affected >=0 <1.6.7

## Details
### Summary

The PROXY command is accepted multiple times, allowing a client to spoof its IP address when the proxy protocol is being used.

### Details

When ProxyOn is enabled, [it looks like the PROXY command will be accepted multiple times](https://github.com/phires/go-guerrilla/blob/fca3b2d8957a746997c7e71fca39004f5c96e91f/server.go#L495), with later invocations overriding earlier ones.  The proxy protocol only supports one initial PROXY header; anything after that is considered part of the exchange between client and server, so the client is free to send further PROXY commands with whatever data it pleases.  go-guerrilla will treat these as coming from the reverse proxy, allowing a client to spoof its IP address.

Note that the format of the PROXY header is [well-defined](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt).  It probably shouldn't be treated as an SMTP command; parsing it the same way is likely to result in odd behavior and could lead to other vulnerabilities.

### PoC

I'm working on writing a PR to fix this vulnerability.  It'll include a unit test that will serve as a PoC on the current version.

### Impact

Any instance with `ProxyOn` enabled (`proxyon` in the JSON config) is affected.

As far as I'm able to tell, the impact is limited to spoofing the `RemoteIP` field.  This isn't ideal, but it probably has less practical impact on an MTA than, say, a web server.

## References
- https://github.com/phires/go-guerrilla/security/advisories/GHSA-c2c3-pqw5-5p7c
- https://nvd.nist.gov/vuln/detail/CVE-2025-31135
- https://github.com/phires/go-guerrilla/commit/7673947f2d5204a135d7ae0b7f80759e548abee6
- https://github.com/phires/go-guerrilla
- https://pkg.go.dev/vuln/GO-2025-3588
