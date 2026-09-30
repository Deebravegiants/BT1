# [M] httpd applies no timeout while receiving a request body, parking a worker on a stalled client

## Summary
Severity: Medium
Advisory: CVE-2026-71380
Aliases: EEF-CVE-2026-71380, GHSA-5vp4-58hc-h8cc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-71380
Type: osv

## Details
Missing Release of Resource after Effective Lifetime vulnerability in Erlang/OTP inets httpd allows an unauthenticated remote attacker to cause denial of service by sending valid request headers with a large Content-Length and then stalling before the body is complete.

httpd_request_handler:handle_info/2 cancels the request timeout as soon as a parse step succeeds, which includes the headers, and the clause that handles a decoder asking for more data re-arms the socket with {active, once} without setting any further timer. httpd_request:whole_body/2 returns such a continuation whenever the bytes received are fewer than the announced Content-Length, so a well-formed request that stops mid-body leaves the worker waiting indefinitely. The periodic byte-rate check that would reclaim it is armed only when minimum_bytes_per_second is configured, which it is not by default. Repeating this across connections occupies every worker permitted by max_clients and denies service to legitimate clients at negligible bandwidth cost.

This issue affects OTP from OTP 17.0 before OTP 27.3.4.17, from OTP 28.0 before OTP 28.5.0.6, and from OTP 29.0 before OTP 29.0.6, corresponding to inets from 5.10 before 9.3.2.7, from 9.4 before 9.6.2.3, and from 9.7 before 9.7.2. Whether OTP before OTP 17.0, corresponding to inets before 5.10, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-71380.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-71380
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71380.json
- https://github.com/erlang/otp/security/advisories/GHSA-5vp4-58hc-h8cc
- https://nvd.nist.gov/vuln/detail/CVE-2026-71380
- https://github.com/erlang/otp/commit/81b453aac5a006bb8d26405f2bc3cf24e9d7733c
- https://github.com/erlang/otp
