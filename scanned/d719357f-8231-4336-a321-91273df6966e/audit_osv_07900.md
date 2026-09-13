# [H] NTLM password overflow via integer overflow

## Summary
Severity: High
Advisory: CURL-CVE-2018-14618
Aliases: CVE-2018-14618
Published: 2018-09-05
Source: https://osv.dev/vulnerability/CURL-CVE-2018-14618
Type: osv

## Details
libcurl contains a buffer overrun in the NTLM authentication code.

The internal function `Curl_ntlm_core_mk_nt_hash` multiplies the `length` of
the password by two (SUM) to figure out how large temporary storage area to
allocate from the heap.

The `length` value is then subsequently used to iterate over the password and
generate output into the allocated storage buffer. On systems with a 32-bit
`size_t`, the math to calculate SUM triggers an integer overflow when the
password length exceeds 2GB (2^31 bytes). This integer overflow usually causes
a tiny buffer to actually get allocated instead of the intended huge one,
making the use of that buffer end up in a heap buffer overflow.

(This bug is almost identical to
[CVE-2017-8816](https://curl.se/docs/CVE-2017-8816.html).)
