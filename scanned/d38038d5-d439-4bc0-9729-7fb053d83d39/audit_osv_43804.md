# [M] inets,httpd: Memory Exhaustion via Unenforced max_body_size During Chunked Body Reception

## Summary
Severity: Medium
Advisory: CVE-2026-74835
Aliases: EEF-CVE-2026-74835, GHSA-8qrh-x566-5xv5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-74835
Type: osv

## Details
The inets application HTTP server httpd fails to enforce a configured body-size limit on chunked request.

This issue affects OTP from OTP 17.0 before OTP 27.3.4.17, from OTP 28.0 before OTP 28.5.0.6, and from OTP 29.0 before OTP 29.0.6, corresponding to inets from 5.10 before 9.3.2.7, from 9.4 before 9.6.2.3, and from 9.7 before 9.7.2. Whether OTP before OTP 17.0, corresponding to inets before 5.10, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-74835.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-74835
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74835.json
- https://github.com/erlang/otp/security/advisories/GHSA-8qrh-x566-5xv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-74835
- https://github.com/erlang/otp/commit/0bceff0c2987cae83d9d4a77c5ecacd6d01b8b86
- https://github.com/erlang/otp/commit/7f9c460d1818c2afb78fbd01f8d8b81343bbb011
- https://github.com/erlang/otp/commit/8e1ca42b64df6c41306affbe8dc129bdbd4042c7
- https://github.com/erlang/otp
