# [H] Tinyproxy - HTTP Request Smuggling via Duplicate Content-Length Headers

## Summary
Severity: High
Advisory: CVE-2026-54388
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-54388
Type: osv

## Details
Tinyproxy through 1.11.3, fixed in commit 364cdb6, fails to reject requests containing multiple Content-Length headers with differing values, forwarding all duplicate headers to the backend while using the first value to determine how many request body bytes to consume. Remote attackers can desynchronize the proxy and backend parser state, allowing injection of arbitrary HTTP requests to the backend to enable cache poisoning, access control bypass, and request hijacking.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54388.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54388
- https://www.vulncheck.com/advisories/tinyproxy-http-request-smuggling-via-duplicate-content-length-headers
- https://github.com/tinyproxy/tinyproxy/issues/609
- https://github.com/tinyproxy/tinyproxy/pull/610
- https://github.com/tinyproxy/tinyproxy/commit/364cdb67e0ea00a8e4a7037e2693e0711e816adb
- https://github.com/tinyproxy/tinyproxy
