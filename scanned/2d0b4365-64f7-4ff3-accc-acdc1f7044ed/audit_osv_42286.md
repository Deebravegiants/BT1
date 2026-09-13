# [M] inets,httpd:HTTP Request Smuggling via obs-fold Header Continuation

## Summary
Severity: Medium
Advisory: CVE-2026-66357
Aliases: EEF-CVE-2026-66357, GHSA-qh2f-33hj-37qf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:L/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-66357
Type: osv

## Details
httpd has never implemented obs-fold (RFC 2616 §2.2 / RFC 7230 §3.2.4 header continuation lines). Every CRLF followed by a non-CRLF octet unconditionally starts a new header. This missing feature became a security concern as the understanding of HTTP request smuggling attacks evolved.

This issue affects OTP from OTP 17.0 before OTP 27.3.4.17, from OTP 28.0 before OTP 28.5.0.6, and from OTP 29.0 before OTP 29.0.6, corresponding to inets from 5.10 before 9.3.2.7, from 9.4 before 9.6.2.3, and from 9.7 before 9.7.2. Whether OTP before OTP 17.0, corresponding to inets before 5.10, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-66357.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-66357
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66357.json
- https://github.com/erlang/otp/security/advisories/GHSA-qh2f-33hj-37qf
- https://nvd.nist.gov/vuln/detail/CVE-2026-66357
- https://github.com/erlang/otp/commit/220d618d2479a7180b4a06d0c5aacfaa4af4a85b
- https://github.com/erlang/otp/commit/273d8958de38ff2a7fe0c5dcc5b6bfe6f65717f3
- https://github.com/erlang/otp/commit/e640d599287d2eba919e6f13b91f042d7dbe6ff4
- https://github.com/erlang/otp
