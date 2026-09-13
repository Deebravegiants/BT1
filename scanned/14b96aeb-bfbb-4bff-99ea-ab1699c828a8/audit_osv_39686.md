# [M] cpp-httplib: Malicious `X-Forwarded-For` Under Trusted-Proxy Configuration Triggers Empty `vector::front()`, Leading to Undefined Behavior and Server Crash

## Summary
Severity: Medium
Advisory: CVE-2026-46527
Aliases: GHSA-hg3g-vrg8-578g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-46527
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. Prior to 0.44.0, When the server has called Server::set_trusted_proxies() with a non-empty trusted-proxy list, an attacker can send an HTTP request that includes an X-Forwarded-For header whose value parses to no valid IP segments. The code path then executes get_client_ip(), which calls front() on an empty std::vector—undefined behavior in C++. On typical implementations this manifests as abnormal process termination (denial of service). With Sanitizers enabled, you get an explicit runtime diagnostic. This vulnerability is fixed in 0.44.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46527.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-hg3g-vrg8-578g
- https://nvd.nist.gov/vuln/detail/CVE-2026-46527
