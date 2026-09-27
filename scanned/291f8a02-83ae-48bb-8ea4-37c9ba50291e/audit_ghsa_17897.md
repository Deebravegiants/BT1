# [M] Eventlet affected by HTTP request smuggling in unparsed trailers

## Summary
Severity: Medium
Advisory: GHSA-hw6f-rjfj-j7j7
CVE: CVE-2025-58068
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-29
Source: https://github.com/advisories/GHSA-hw6f-rjfj-j7j7
Type: github-advisory

## Affected
- PyPI: `eventlet` — affected >=0 <0.40.3

## Details
### Impact
The Eventlet WSGI parser is vulnerable to HTTP Request Smuggling due to improper handling of HTTP trailer sections.

This vulnerability could enable attackers to:
- Bypass front-end security controls
- Launch targeted attacks against active site users
- Poison web caches

### Patches
Problem has been patched in eventlet 0.40.3.

The patch just drops trailers. If a backend behind eventlet.wsgi proxy requires trailers, then this patch BREAKS your setup.

### Workarounds
Do not use eventlet.wsgi facing untrusted clients.

### References
- Patch https://github.com/eventlet/eventlet/pull/1062
- This issue is similar to https://github.com/advisories/GHSA-9548-qrrj-x5pj

## References
- https://github.com/eventlet/eventlet/security/advisories/GHSA-hw6f-rjfj-j7j7
- https://nvd.nist.gov/vuln/detail/CVE-2025-58068
- https://github.com/eventlet/eventlet/pull/1062
- https://github.com/eventlet/eventlet/commit/0bfebd1117d392559e25b4bfbfcc941754de88fb
- https://github.com/eventlet/eventlet
- https://lists.debian.org/debian-lts-announce/2025/09/msg00003.html
