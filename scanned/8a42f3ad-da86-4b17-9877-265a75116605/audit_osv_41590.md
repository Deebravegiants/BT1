# [M] Netty 4.2.0 through 4.2.16 TLS Hostname Verification Bypass

## Summary
Severity: Medium
Advisory: CVE-2026-62243
Aliases: GHSA-p85m-gvr3-788c
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-62243
Type: osv

## Details
Netty (io.netty:netty-handler) versions from 4.2.0.Final through 4.2.16.Final and versions through 4.1.136.Final disable TLS hostname verification on the SslProvider.OPENSSL client path when a plain (non-extended) X509TrustManager is used and Unsafe-based trust-manager wrapping is unavailable (Java 25+). In this configuration the OpenSSL client does not perform hostname verification, allowing a man-in-the-middle attacker to present a certificate issued for a different hostname that is accepted without validation. Fixed in 4.2.17.Final and 4.1.137.Final.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62243.json
- https://github.com/netty/netty/security/advisories/GHSA-p85m-gvr3-788c
- https://nvd.nist.gov/vuln/detail/CVE-2026-62243
- https://www.vulncheck.com/advisories/netty-through-tls-hostname-verification-bypass
