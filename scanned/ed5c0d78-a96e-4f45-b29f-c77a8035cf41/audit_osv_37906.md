# [H] cpp-httplib Client Leaks Authentication Credentials to Untrusted Hosts on Cross-Origin HTTP Redirect

## Summary
Severity: High
Advisory: CVE-2026-33745
Aliases: GHSA-6hrp-7fq9-3qv2
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-33745
Type: osv

## Details
cpp-httplib is a C++11 single-file header-only cross platform HTTP/HTTPS library. Prior to 0.39.0, the cpp-httplib HTTP client forwards stored Basic Auth, Bearer Token, and Digest Auth credentials to arbitrary hosts when following cross-origin HTTP redirects (301/302/307/308). A malicious or compromised server can redirect the client to an attacker-controlled host, which then receives the plaintext credentials in the `Authorization` header. Version 0.39.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33745.json
- https://github.com/yhirose/cpp-httplib/security/advisories/GHSA-6hrp-7fq9-3qv2
- https://nvd.nist.gov/vuln/detail/CVE-2026-33745
