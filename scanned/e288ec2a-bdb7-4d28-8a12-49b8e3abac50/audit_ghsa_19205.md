# [H] Mitmweb API Authentication Bypass Using Proxy Server

## Summary
Severity: High
Advisory: GHSA-wg33-5h85-7q5p
CVE: CVE-2025-23217
CWE: CWE-288, CWE-441
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-wg33-5h85-7q5p
Type: github-advisory

## Affected
- PyPI: `mitmproxy` — affected >=0 <11.1.2

## Details
### Impact
In mitmweb 11.1.0 and below, a malicious client can use mitmweb's proxy server (bound to `*:8080` by default) to access mitmweb's internal API (bound to `127.0.0.1:8081` by default). In other words, while the client cannot access the API directly (good), they can access the API through the proxy (bad). An attacker may be able to escalate this [SSRF](https://en.wikipedia.org/wiki/Server-side_request_forgery)-style access to remote code execution.

The mitmproxy and mitmdump tools are unaffected. Only mitmweb is affected. The `block_global` option, which is enabled by default, blocks connections originating from publicly-routable IP addresses in the proxy. The attacker needs to be in the same local network.

### Patches

The vulnerability has been fixed in mitmproxy 11.1.2 and above.

### Acknowledgements

We thank Stefan Grönke (@gronke) for reporting this vulnerability as part of a security audit by [Radically Open Security](https://www.radicallyopensecurity.com/). This audit was supported by the [NGI0 Entrust fund](https://nlnet.nl/entrust/) established by [NLnet](https://nlnet.nl/).

### Timeline

- **2025-01-14**: Received initial report. 
- **2025-01-14**: Verified report and confirmed receipt.
- **2025-01-19**: Shared patch with researcher.
- **2025-02-04**: Received final confirmation that patch is working.
- **2025-02-05**: Published patched release and advisory.

## References
- https://github.com/mitmproxy/mitmproxy/security/advisories/GHSA-wg33-5h85-7q5p
- https://nvd.nist.gov/vuln/detail/CVE-2025-23217
- https://github.com/mitmproxy/mitmproxy/commit/fa89055e196d953f11fd241e36ee37858993486a
- https://en.wikipedia.org/wiki/Server-side_request_forgery
- https://github.com/mitmproxy/mitmproxy
- https://github.com/mitmproxy/mitmproxy/blob/main/CHANGELOG.md
- https://github.com/mitmproxy/mitmproxy/blob/main/CHANGELOG.md#06-february-2025-mitmproxy-1112
