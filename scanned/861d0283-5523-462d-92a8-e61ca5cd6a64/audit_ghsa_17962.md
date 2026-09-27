# [M] request-filtering-agent SSRF Bypass via HTTPS Requests to 127.0.0.1

## Summary
Severity: Medium
Advisory: GHSA-pw25-c82r-75mm
CVE: CVE-2025-57814
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N/E:P (CVSS_V4)
Published: 2025-08-25
Source: https://github.com/advisories/GHSA-pw25-c82r-75mm
Type: github-advisory

## Affected
- npm: `request-filtering-agent` — affected >=0 <2.0.0

## Details
request-filtering-agent versions 1.x.x and earlier contain a vulnerability where HTTPS requests to 127.0.0.1 bypass IP address filtering, while HTTP requests are correctly blocked.

**Impact:**

Vulnerable patterns (requests that should be blocked but are allowed):
- https://127.0.0.1:443/api
- https://127.0.0.1:8443/admin
- Any HTTPS request using direct IP address `https://127.0.0.1`

This vulnerability primarily affects services using self-signed certificates on `127.0.0.1`.

**Not affected (correctly blocked in all versions):**
- http://127.0.0.1:80/api - HTTP requests are properly blocked
- https://localhost:443/api - Domain-based requests trigger DNS lookup and are blocked
- http://localhost:80/api - Domain-based HTTP requests are blocked
- Requests to other private IPs like 192.168.x.x, 10.x.x.x, 172.16.x.x

This allows attackers to potentially access internal HTTPS services running on localhost, bypassing the library's SSRF protection. The vulnerability is particularly dangerous when the application accepts user-controlled URLs and internal services are only protected by network-level restrictions.

## Fixed in 2.0.0

This vulnerability has been fixed in request-filtering-agent version 2.0.0. Users should upgrade to version 2.0.0 or later.

Root Cause:The HTTPS agent fails to validate direct IP addresses like `https://127.0.0.1` during TLS connection setup, allowing them to bypass the security filter.

Details: https://github.com/azu/request-filtering-agent-https127-test

Thanks Luca

## References
- https://github.com/azu/request-filtering-agent/security/advisories/GHSA-pw25-c82r-75mm
- https://nvd.nist.gov/vuln/detail/CVE-2025-57814
- https://github.com/azu/request-filtering-agent
- https://github.com/azu/request-filtering-agent-https127-test
