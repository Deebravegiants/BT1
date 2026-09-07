# [H] Steeltoe vulnerable to management-port isolation bypass via spoofed Host header

## Summary
Severity: High
Advisory: GHSA-58f6-6rj2-3v8r
CVE: CVE-2026-50194
CWE: CWE-288, CWE-639
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-58f6-6rj2-3v8r
Type: github-advisory

## Affected
- NuGet: `Steeltoe.Management.Endpoint` — affected >=0 <4.2.0
- NuGet: `Steeltoe.Management.EndpointCore` — affected >=3.2.2 <3.4.0

## Details
### Summary

When Steeltoe management endpoints are configured to listen on an alternate port (`Management:Endpoints:Port` is configured), the middleware responsible for restricting access to the endpoints uses the `Host` HTTP header rather than the actual network socket port. 

### Impact

An unauthenticated remote attacker can reach every actuator endpoint using a specially crafted HTTP request.

### Affected configuration

- The application's public port is accessible over from the network.
- `Management:Endpoints:Port` is configured to a value different from the application's main listener port.
- The request scheme matches `Management:Endpoints:SslEnabled`. For example, `http` when `SslEnabled` is `false` (the default), or `https` when `SslEnabled` is `true`.

### Mitigations

If an immediate upgrade to a patched version is not possible:

- Add explicit ASP.NET Core authorization (`RequireAuthorization`) to all sensitive actuator endpoints as a defense-in-depth measure independent of port isolation.
- Configure the reverse proxy or load balancer to enforce the `Host` header value and prevent clients from setting an arbitrary port.

## References
- https://github.com/SteeltoeOSS/security-advisories/security/advisories/GHSA-58f6-6rj2-3v8r
- https://nvd.nist.gov/vuln/detail/CVE-2026-50194
- https://github.com/SteeltoeOSS/Steeltoe/commit/4cbc352fe89ac2e6c609554e435ab28996fec5e9
- https://github.com/SteeltoeOSS/Steeltoe/commit/b7ca93c510aaa08d7e4ebec40ce20c5811c2c4b6
- https://github.com/SteeltoeOSS/steeltoe
