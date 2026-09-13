# [H] Netty: Wrapping plain trust manager silently disables hostname verification

## Summary
Severity: High
Advisory: GHSA-c653-97m9-rcg9
CVE: CVE-2026-50010
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-c653-97m9-rcg9
Type: github-advisory

## Affected
- Maven: `io.netty:netty-handler` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-handler` — affected >=0 <4.1.135.Final

## Details
SimpleTrustManagerFactory.engineGetTrustManagers() and related paths wrap any user-supplied plain X509TrustManager in X509TrustManagerWrapper, which extends X509ExtendedTrustManager but implements the 3-arg checkServerTrusted(chain, authType, SSLEngine) by discarding the SSLEngine and calling the 2-arg delegate. Because the object now IS an X509ExtendedTrustManager, neither SunJSSE's internal AbstractTrustManagerWrapper nor Netty's own OpenSslX509TrustManagerWrapper will re-wrap it to add endpoint-identification. Consequently, even though Netty 4.2 sets endpointIdentificationAlgorithm="HTTPS" by default, a client built with `SslContextBuilder.forClient().trustManager(somePlainX509TrustManager)` performs no hostname verification at all.

## References
- https://github.com/netty/netty/security/advisories/GHSA-c653-97m9-rcg9
- https://nvd.nist.gov/vuln/detail/CVE-2026-50010
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
