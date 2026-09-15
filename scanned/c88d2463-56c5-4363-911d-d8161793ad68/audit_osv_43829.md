# [M] inets, httpd: Authentication Bypass via Directory Namespace Collapse in httpd mod_auth

## Summary
Severity: Medium
Advisory: CVE-2026-74994
Aliases: EEF-CVE-2026-74994, GHSA-c3cq-q8x6-547g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-74994
Type: osv

## Details
The mod_auth module in OTP's inets httpd server, when configured with dets or mnesia authentication backends and multiple directory configuration blocks, collapses all directory blocks into a single shared user/group namespace. A user added to one protected directory is accepted as valid for all other protected directories on the same server instance.

This issue affects OTP from OTP 17.0 before OTP 27.3.4.17, from OTP 28.0 before OTP 28.5.0.6, and from OTP 29.0 before OTP 29.0.6, corresponding to inets from 5.10 before 9.3.2.7, from 9.4 before 9.6.2.3, and from 9.7 before 9.7.2. Whether OTP before OTP 17.0, corresponding to inets before 5.10, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-74994.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-74994
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74994.json
- https://github.com/erlang/otp/security/advisories/GHSA-c3cq-q8x6-547g
- https://nvd.nist.gov/vuln/detail/CVE-2026-74994
- https://github.com/erlang/otp/commit/6101cb74ff2870718c622ba7af0c100f7f2524e3
- https://github.com/erlang/otp/commit/6982e381137ede21a4e1faf5fa2dd82321691176
- https://github.com/erlang/otp/commit/c5ccec8ed25c70ec6557fd81277e4b2f52285c19
- https://github.com/erlang/otp
