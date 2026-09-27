# [M] httpc memory exhaustion via unbounded response header accumulation

## Summary
Severity: Medium
Advisory: CVE-2026-55951
Aliases: EEF-CVE-2026-55951, GHSA-f9fw-mg7q-4g3x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-55951
Type: osv

## Details
The Erlang/OTP httpc HTTP client does not enforce a limit on the total size of response headers received from a server. The max_header_size option defaults to nolimit, and httpc_response:parse_headers/6 accumulates every header into a list before the length check runs (which only fires after the terminating CRLF CRLF is received).

A malicious or compromised HTTP server can send an arbitrarily large number of headers, or headers with very large values, causing the client process to allocate unbounded memory until the system runs out of memory or the BEAM VM crashes. A proof-of-concept server sending 100,000 headers of roughly 4000 bytes each caused the client VM to allocate over 13 GB of memory in under 30 seconds.

Any application using httpc:request/4,5 to connect to untrusted servers is affected. No authentication is required: any server the client connects to (including via a redirect or man-in-the-middle) can trigger the exhaustion.

This issue affects OTP from OTP 17.0 before OTP 27.3.4.17, from OTP 28.0 before OTP 28.5.0.6, and from OTP 29.0 before OTP 29.0.6, corresponding to inets from 5.10 before 9.3.2.7, from 9.4 before 9.6.2.3, and from 9.7 before 9.7.2. Whether OTP before OTP 17.0, corresponding to inets before 5.10, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-55951.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-55951
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55951.json
- https://github.com/erlang/otp/security/advisories/GHSA-f9fw-mg7q-4g3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-55951
- https://github.com/erlang/otp/commit/aba0fe8c2d700bf4ac94607cf7f00e53bbe4042d
- https://github.com/erlang/otp/commit/e3be1cfe9f6cedd0cd20d9905e05601dfb31c8aa
- https://github.com/erlang/otp
