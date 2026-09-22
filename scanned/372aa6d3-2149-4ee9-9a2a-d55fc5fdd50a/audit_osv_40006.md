# [M] httpc leaks Authorization header to cross-origin redirect targets

## Summary
Severity: Medium
Advisory: CVE-2026-48856
Aliases: EEF-CVE-2026-48856, GHSA-m75x-4vwg-ggjh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-48856
Type: osv

## Details
Sensitive Data Exposure vulnerability in Erlang OTP inets (httpc_response module) allows Retrieve Embedded Sensitive Data.

The httpc client forwards the Authorization and Proxy-Authorization request headers to redirect targets without checking whether the redirect crosses an origin boundary. httpc_response:redirect/2 constructs the redirected request by updating only the host field of the header record; all other fields (including authorization and proxy_authorization) are copied verbatim. The redirect target host is never compared against the original host.

autoredirect defaults to true, so this affects all httpc callers that do not explicitly disable automatic redirects.

An attacker who controls a server that the victim contacts via httpc can issue a cross-origin 3xx redirect to a server they also control. The Authorization header (including Basic credentials derived from URL userinfo via httpc_request:handle_user_info/2) is forwarded to the redirect target, allowing credential theft. The same applies to the Proxy-Authorization header.

This vulnerability is associated with program files lib/inets/src/http_client/httpc_response.erl.

This issue affects OTP from OTP 17.0 before OTP 29.0.2, OTP 28.5.0.2 and OTP 27.3.4.13, corresponding to inets from 5.10 before 9.7.1, 9.6.2.2 and 9.3.2.6.

## References
- https://cna.erlef.org/cves/CVE-2026-48856.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-48856
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48856.json
- https://github.com/erlang/otp/security/advisories/GHSA-m75x-4vwg-ggjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-48856
- https://github.com/erlang/otp/commit/688d748d6f7a6a06b13b662a1d3de8af97079612
- https://github.com/erlang/otp
