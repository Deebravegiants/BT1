# [C] sctp: validate cached peer INIT chunk length in COOKIE_ECHO processing

## Summary
Severity: Critical
Advisory: CVE-2026-53246
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53246
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: validate cached peer INIT chunk length in COOKIE_ECHO processing

When a listening SCTP server processes a COOKIE_ECHO chunk, the cached
peer INIT chunk embedded after the cookie is parsed and its parameters
are later walked by sctp_process_init() using sctp_walk_params().

However, the chunk header length of this cached INIT chunk was not
validated against the remaining buffer in the COOKIE_ECHO payload. If
the length field is inflated, the parameter walk can run beyond the
actual received data, leading to out-of-bounds reads and potential
memory corruption during later parameter handling (e.g. STATE_COOKIE
processing and kmemdup() copies).

Add a bounds check in sctp_unpack_cookie() to ensure the cached INIT
chunk length does not exceed the available data in the COOKIE_ECHO
buffer before it is used.

## References
- https://git.kernel.org/stable/c/0861615c28de668669d748ef4eb913ea9262d13b
- https://git.kernel.org/stable/c/cc272185c9a9a4b7febc2de52eeaa3d00f19091e
- https://git.kernel.org/stable/c/edccbf3d63b0a3362bc916ea72edacc1e1ca456a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53246.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53246
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
