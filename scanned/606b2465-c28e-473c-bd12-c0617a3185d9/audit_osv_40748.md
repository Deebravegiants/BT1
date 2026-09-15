# [M] BEAM VM crash via integer underflow in binary_to_term BIT_BINARY_EXT decoding

## Summary
Severity: Medium
Advisory: CVE-2026-54890
Aliases: EEF-CVE-2026-54890, GHSA-54pw-5645-jh86
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-54890
Type: osv

## Details
Integer Underflow (Wrap or Wraparound) vulnerability in erlang otp erlang/otp (erts modules), erlang otp erts (erts modules) allows Forced Integer Overflow, Excessive Allocation. This vulnerability is associated with program files erts/emulator/beam/external.c, emulator/beam/external.c.

The BIT_BINARY_EXT tag (77) handler in the External Term Format (ETF) decoder accepts an encoding with both length and trailing-bits fields set to zero. The subsequent computation of the bitstring size underflows an unsigned integer, producing a value of roughly 2^64 that is then passed as a memory allocation size. The allocator aborts the entire node with a message such as "Cannot allocate 2305843009213693951 bytes of memory (of type binary)".

The crash is a VM-level abort, not an Erlang-level exception. It cannot be intercepted by supervision trees, by try/catch, or by passing the [safe] option to binary_to_term/2 (which only restricts atom creation and does not perform structural validation of binary encodings).

Any application that decodes ETF from untrusted sources via binary_to_term/1,2 or enif_binary_to_term() is exposed. The Erlang distribution protocol also decodes incoming terms through the same code path, but distribution is expected to run on trusted networks per the OTP Secure Coding Guidelines (DSG-011).

This issue affects OTP from OTP 27.0 before OTP 29.0.4, OTP 28.5.0.4 and OTP 27.3.4.15, corresponding to erts from 15.0 before 17.0.4, 16.4.0.4 and 15.2.7.11.

## References
- https://cna.erlef.org/cves/CVE-2026-54890.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-54890
- https://www.erlang.org/doc/system/versions.html#order-of-versions
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54890.json
- https://github.com/erlang/otp/security/advisories/GHSA-54pw-5645-jh86
- https://nvd.nist.gov/vuln/detail/CVE-2026-54890
- https://github.com/erlang/otp/commit/dc1bf9344c0ce62717cf60866590cea0242780fd
- https://github.com/erlang/otp
