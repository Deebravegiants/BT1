# [H] sctp: fix auth_hmacs array size in struct sctp_cookie

## Summary
Severity: High
Advisory: CVE-2026-68376
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68376
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.24 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: fix auth_hmacs array size in struct sctp_cookie

The auth_hmacs array in struct sctp_cookie is supposed to store a complete
SCTP_AUTH_HMAC_ALGO parameter, which consists of a struct sctp_paramhdr
followed by N HMAC identifiers.

However, the array size was calculated using an extra 2 bytes instead of
sizeof(struct sctp_paramhdr), which is 4 bytes. When four HMAC identifiers
are configured, the HMAC-ALGO parameter stored in the endpoint is larger
than the auth_hmacs buffer in the cookie.

As a result, sctp_association_init() copies beyond the end of auth_hmacs
when initializing the association, corrupting the adjacent auth_chunks
field. This can lead to an invalid HMAC identifier being accepted and later
cause an out-of-bounds read in sctp_auth_get_hmac().

Fix the array size calculation by including the full SCTP parameter header
size.

## References
- https://git.kernel.org/stable/c/0528485f27016a42804abe01aa61b39d85fa803e
- https://git.kernel.org/stable/c/0b4414e43e0861d67276031cc21401d7e87de3da
- https://git.kernel.org/stable/c/317731d01b03c529809df36d3a7d149677a8729d
- https://git.kernel.org/stable/c/3aa40c3bccac2312ea7cf97f329190637f972b5d
- https://git.kernel.org/stable/c/a8d20ba0ab518c9ccbcde258f25fc1ee6e51d5db
- https://git.kernel.org/stable/c/d0a59ba58578e2b330fff80a44fe519f3ba7d8c7
- https://git.kernel.org/stable/c/e0b5252a59383b77d1b8dbeda00b7184dd95f4d3
- https://git.kernel.org/stable/c/ee5e65964f456adfe14d526fba0bd055de98ecf3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68376.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68376
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
