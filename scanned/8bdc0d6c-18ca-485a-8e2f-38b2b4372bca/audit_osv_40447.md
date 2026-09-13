# [C] sctp: validate embedded INIT chunk and address list lengths in cookie

## Summary
Severity: Critical
Advisory: CVE-2026-53224
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53224
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: validate embedded INIT chunk and address list lengths in cookie

sctp_unpack_cookie() only checked that the embedded INIT chunk length
did not exceed the remaining cookie payload, but did not ensure that the
INIT chunk is large enough to contain a complete INIT header.

A malformed COOKIE_ECHO can therefore carry a truncated INIT chunk whose
length field is smaller than sizeof(struct sctp_init_chunk).  Later,
sctp_process_init() accesses INIT parameters unconditionally, which may
lead to out-of-bounds reads.

In addition, raw_addr_list_len is not fully validated against the
remaining cookie payload. When cookie authentication is disabled, an
attacker can supply an oversized raw_addr_list_len and cause
sctp_raw_to_bind_addrs() to read beyond the end of the cookie. The
address parser also lacks sufficient bounds checks for parameter headers
and lengths, allowing malformed address parameters to trigger
out-of-bounds reads.

Fix this by:

- requiring the embedded INIT chunk length to be at least sizeof(struct
  sctp_init_chunk);
- validating that the INIT chunk and raw address list together fit
  within the cookie payload;
- verifying sufficient data exists for each address parameter header and
  payload before parsing it.

Note that sctp_verify_init() must be called after sctp_unpack_cookie()
and before sctp_process_init() when cookie authentication is disabled.
This will be addressed in a separate patch.

## References
- https://git.kernel.org/stable/c/512a9bb77c04ac9927648ea58af617e472be96e6
- https://git.kernel.org/stable/c/6f4c80a2a7e6d06753b89a578b710a2499a5e62b
- https://git.kernel.org/stable/c/7560afb8cddafd829e709d7ea09230e45a825557
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53224.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53224
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
