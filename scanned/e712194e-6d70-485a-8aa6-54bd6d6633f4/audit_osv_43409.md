# [M] inets, httpd: HTTP Request Smuggling via Transfer-Encoding and Content-Length

## Summary
Severity: Medium
Advisory: CVE-2026-73812
Aliases: EEF-CVE-2026-73812, GHSA-7j6m-4ffg-hg46
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-73812
Type: osv

## Details
httpd function check_header/3 rejects duplicate Content-Length (per CVE-2026-23941) but never checks for the TE+CL co-presence that RFC 9112 §6.3 identifies as a probable smuggling attempt. handle_body/3 frames by chunked and silently discards Content-Length. A CL-preferring front-end paired with chunked-preferring inets creates a classic CL.TE front-end/back-end desync.

This issue affects OTP from OTP 17.0 before OTP 27.3.4.17, from OTP 28.0 before OTP 28.5.0.6, and from OTP 29.0 before OTP 29.0.6, corresponding to inets from 5.10 before 9.3.2.7, from 9.4 before 9.6.2.3, and from 9.7 before 9.7.2. Whether OTP before OTP 17.0, corresponding to inets before 5.10, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-73812.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-73812
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73812.json
- https://github.com/erlang/otp/security/advisories/GHSA-7j6m-4ffg-hg46
- https://nvd.nist.gov/vuln/detail/CVE-2026-73812
- https://github.com/erlang/otp/commit/591dc00dc99dc2a426167a3b5257c0c94bd45e91
- https://github.com/erlang/otp
