# [H] CVE-2021-47107

## Summary
Severity: High
Advisory: CVE-2021-47107
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47107
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Fix READDIR buffer overflow

If a client sends a READDIR count argument that is too small (say,
zero), then the buffer size calculation in the new init_dirlist
helper functions results in an underflow, allowing the XDR stream
functions to write beyond the actual buffer.

This calculation has always been suspect. NFSD has never sanity-
checked the READDIR count argument, but the old entry encoders
managed the problem correctly.

With the commits below, entry encoding changed, exposing the
underflow to the pointer arithmetic in xdr_reserve_space().

Modern NFS clients attempt to retrieve as much data as possible
for each READDIR request. Also, we have no unit tests that
exercise the behavior of READDIR at the lower bound of @count
values. Thus this case was missed during testing.

## References
- https://git.kernel.org/stable/c/53b1119a6e5028b125f431a0116ba73510d82a72
- https://git.kernel.org/stable/c/9e291a6a28d32545ed2fd959a8165144d1724df1
- https://git.kernel.org/stable/c/eabc0aab98e5218ceecd82069b0d6fdfff5ee885
