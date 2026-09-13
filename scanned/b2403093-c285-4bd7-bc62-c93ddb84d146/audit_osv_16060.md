# [H] CVE-2019-25219

## Summary
Severity: High
Advisory: CVE-2019-25219
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2019-25219
Type: osv

## Details
Asio C++ Library before 1.13.0 lacks a fallback error code in the case of SSL_ERROR_SYSCALL with no associated error information from the SSL library being used.

## References
- https://github.com/chriskohlhoff/asio/compare/asio-1-12-2...asio-1-13-0
- https://think-async.com/Asio/
- https://github.com/chriskohlhoff/asio/commit/93337cba7b013150f5aa6194393e1d94be2853ec
