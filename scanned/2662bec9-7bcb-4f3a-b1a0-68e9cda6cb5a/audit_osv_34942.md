# [M] cpp-httplib Untrusted HTTP Header Handling: X-Forwarded-For/X-Real-IP Trust

## Summary
Severity: Medium
Advisory: CVE-2025-66577
Aliases: GHSA-gfpf-r66f-5mh2
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-12-05
Source: https://osv.dev/vulnerability/CVE-2025-66577
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. Prior to 0.27.0, a vulnerability allows attacker-controlled HTTP headers to influence server-visible metadata, logging, and authorization decisions. An attacker can supply X-Forwarded-For or X-Real-IP headers which get accepted unconditionally by get_client_ip() in docker/main.cc, causing access and error logs (nginx_access_logger / nginx_error_logger) to record spoofed client IPs (log poisoning / audit evasion). This vulnerability is fixed in 0.27.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66577.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-gfpf-r66f-5mh2
- https://nvd.nist.gov/vuln/detail/CVE-2025-66577
- https://github.com/yhirose/cpp-httplib/commit/ac9ebb0ee333ce8bf13523f487bdfad9518a2aff
