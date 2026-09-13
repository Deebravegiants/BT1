# [M] one-api through 0.6.10 Missing Authorization on URL-Parameter Channel Pinning

## Summary
Severity: Medium
Advisory: CVE-2026-81027
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-81027
Type: osv

## Details
one-api gates one of its two channel-pinning paths and not the other. middleware/auth.go permits a request to name a specific channel either through a suffix on the API key or through a URL path parameter. The suffix path is reached only after model.IsAdmin succeeds and otherwise rejects the caller, while the path-parameter branch sets the selected-channel value from c.Param("channelid") with no role check at all. The route carrying that parameter sits behind token authentication only, so any account holding a valid API token reaches it. The value flows to the distributor, which loads the channel by integer identifier with no scoping to the caller's user or group, and then sets the outbound Authorization header to that channel's stored key and directs the request at the channel's base URL. A low-privilege account can therefore pin any channel by incrementing an identifier, causing the server to make upstream requests bearing an operator-configured provider key the account was never granted, and bypassing both the per-group restriction and the channel's model allowlist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81027.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81027
- https://www.vulncheck.com/advisories/one-api-through-0.6.10-missing-authorization-on-url-parameter-channel-pinning
- https://github.com/songquanpeng/one-api/issues/2410
- https://github.com/songquanpeng/one-api
- https://github.com/songquanpeng/one-api/blob/v0.6.10/middleware/auth.go
