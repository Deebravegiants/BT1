# [M] inets, httpd: HTTP Request Smuggling via Whitespace-Before-Colon Header Dropping i

## Summary
Severity: Medium
Advisory: CVE-2026-73276
Aliases: EEF-CVE-2026-73276, GHSA-6v7q-jwgh-cx8p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-73276
Type: osv

## Details
Gracefulness code ignored cases that should be rejected, resulting in possible HTTP Request Smuggling opportunities.

This issue affects OTP from OTP 22.2 before OTP 27.3.4.17, from OTP 28.0 before OTP 28.5.0.6, and from OTP 29.0 before OTP 29.0.6, corresponding to inets from 7.1.2 before 9.3.2.7, from 9.4 before 9.6.2.3, and from 9.7 before 9.7.2.

## References
- https://cna.erlef.org/cves/CVE-2026-73276.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-73276
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73276.json
- https://github.com/erlang/otp/security/advisories/GHSA-6v7q-jwgh-cx8p
- https://nvd.nist.gov/vuln/detail/CVE-2026-73276
- https://github.com/erlang/otp/commit/60add5a19e2154560fdff3fe92dba14a68bbd683
- https://github.com/erlang/otp/commit/6cd995e34d3bb3d36dd278dded2d62c25e71820c
- https://github.com/erlang/otp/commit/c285240c6e4b93960c5dc4f17ba04e6fdfb27a0f
- https://github.com/erlang/otp
