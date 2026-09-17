# [M] Stack Buffer Overflow in ei_s_print_term at Very Large Integer

## Summary
Severity: Medium
Advisory: CVE-2026-49760
Aliases: EEF-CVE-2026-49760, GHSA-xcxj-5pg2-v72j
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-49760
Type: osv

## Details
Stack-based Buffer Overflow vulnerability in Erlang OTP (erl_interface) allows Stack-based Buffer Overflow.

This vulnerability is associated with program file lib/erl_interface/src/misc/ei_printterm.c and program routine ei_s_print_term.

The C function ei_s_print_term uses an internal 2000-character stack buffer to format terms. When called with an encoded Erlang term containing a very large integer (encoded representation exceeding 2000 characters), the buffer overflows. The overflow bytes are restricted to the ASCII values of 0-9 and A-F, which limits exploitation to Denial of Service.

The companion function ei_print_term, which prints directly to a FILE instead of a memory buffer, does not contain this bug.

This issue affects OTP from OTP 17.0 before OTP 29.0.2, OTP 28.5.0.2 and OTP 27.3.4.13, corresponding to erl_interface from 3.7.16 before 5.8.1, 5.7.0.1 and 5.5.2.1.

## References
- https://cna.erlef.org/cves/CVE-2026-49760.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-49760
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/49xxx/CVE-2026-49760.json
- https://github.com/erlang/otp/security/advisories/GHSA-xcxj-5pg2-v72j
- https://nvd.nist.gov/vuln/detail/CVE-2026-49760
- https://github.com/erlang/otp/commit/0bef277b2d39dc8babb9ceb4f5d0a456f3007111
- https://github.com/erlang/otp
