# [M] msgpack-c Integer Overflow in msgpack_unpacker_expand_buffer Causes a False-Success Undersized Reservation

## Summary
Severity: Medium
Advisory: CVE-2026-72854
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:P/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/CVE-2026-72854
Type: osv

## Details
msgpack_unpacker_expand_buffer in src/unpack.c, reached through the public msgpack_unpacker_reserve_buffer API, computes its new buffer size using an unchecked size_t addition of the requested size and the amount already used. The doubling loop guards its own multiplication against overflow, but the addition in the loop condition is unguarded, so a request near SIZE_MAX wraps: the loop condition is already satisfied, the allocation is performed at the small pre-wrap size, and the function returns true. The caller is told the requested capacity was reserved when it was not, so a subsequent write of the requested length overflows the heap buffer. The library's own example/lib_buffer_unpack.c demonstrates the reserve-then-write pattern, and its defensive assert comparing capacity against the request is compiled out under NDEBUG. msgpack-c's own decode entry points do not derive the reservation size from untrusted input, so reaching this requires an integration that passes an attacker-influenced length to the reservation API, such as a length-prefixed streaming transport.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72854.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72854
- https://www.vulncheck.com/advisories/msgpack-c-integer-overflow-in-msgpack-unpacker-expand-buffer-causes-a-false-success-undersized-reservation
- https://github.com/msgpack/msgpack-c/issues/1181
- https://github.com/msgpack/msgpack-c
- https://github.com/msgpack/msgpack-c/blob/c-7.0.1/example/lib_buffer_unpack.c
- https://github.com/msgpack/msgpack-c/blob/c-7.0.1/include/msgpack/unpack.h#L219-L223
- https://github.com/msgpack/msgpack-c/blob/c-7.0.1/src/unpack.c#L429-L502
