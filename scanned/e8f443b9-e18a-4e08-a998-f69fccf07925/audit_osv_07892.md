# [M] NTLM buffer overflow via integer overflow

## Summary
Severity: Medium
Advisory: CURL-CVE-2017-8816
Aliases: CVE-2017-8816
Published: 2017-11-29
Source: https://osv.dev/vulnerability/CURL-CVE-2017-8816
Type: osv

## Details
libcurl contains a buffer overrun flaw in the NTLM authentication code.

The internal function `Curl_ntlm_core_mk_ntlmv2_hash` sums up the lengths of
the username + password (= SUM) and multiplies the sum by two (= SIZE) to
figure out how large storage to allocate from the heap.

The SUM value is subsequently used to iterate over the input and generate
output into the storage buffer. On systems with a 32-bit `size_t`, the math to
calculate SIZE triggers an integer overflow when the combined lengths of the
username and password is larger than 2GB (2^31 bytes). This integer overflow
usually causes a tiny buffer to actually get allocated instead of the intended
huge one, making the use of that buffer end up in a buffer overrun.
