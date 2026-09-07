# [H] SslHandler doesn't correctly validate packets which can lead to native crash when using native SSLEngine

## Summary
Severity: High
Advisory: GHSA-4g8c-wm8x-jfhw
CVE: CVE-2025-24970
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-10
Source: https://github.com/advisories/GHSA-4g8c-wm8x-jfhw
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler` — affected >=4.1.91.Final <4.1.118.Final

## Details
### Impact
When a special crafted packet is received via SslHandler it doesn't correctly handle validation of such a packet in all cases which can lead to a native crash.

### Workarounds
As workaround its possible to either disable the usage of the native SSLEngine or changing the code from:

```
SslContext context = ...;
SslHandler handler = context.newHandler(....);
```

to:

```
SslContext context = ...;
SSLEngine engine = context.newEngine(....);
SslHandler handler = new SslHandler(engine, ....);
```

## References
- https://github.com/netty/netty/security/advisories/GHSA-4g8c-wm8x-jfhw
- https://nvd.nist.gov/vuln/detail/CVE-2025-24970
- https://github.com/netty/netty/commit/87f40725155b2f89adfde68c7732f97c153676c4
- https://github.com/netty/netty
- https://security.netapp.com/advisory/ntap-20250221-0005
- https://www.vicarius.io/vsociety/posts/cve-2025-24970-netty-vulnerability-detection
- https://www.vicarius.io/vsociety/posts/cve-2025-24970-netty-vulnerability-mitigation
