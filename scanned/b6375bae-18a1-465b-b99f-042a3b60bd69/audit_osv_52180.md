# [M] CVE-2021-47168

## Summary
Severity: Medium
Advisory: CVE-2021-47168
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47168
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: fix an incorrect limit in filelayout_decode_layout()

The "sizeof(struct nfs_fh)" is two bytes too large and could lead to
memory corruption.  It should be NFS_MAXFHSIZE because that's the size
of the ->data[] buffer.

I reversed the size of the arguments to put the variable on the left.

## References
- https://git.kernel.org/stable/c/f299522eda1566cbfbae4b15c82970fc41b03714
- https://git.kernel.org/stable/c/769b01ea68b6c49dc3cde6adf7e53927dacbd3a8
- https://git.kernel.org/stable/c/945ebef997227ca8c20bad7f8a8358c8ee57a84a
- https://git.kernel.org/stable/c/9b367fe770b1b80d7bf64ed0d177544a44405f6e
- https://git.kernel.org/stable/c/9d280ab53df1d4a1043bd7a9e7c6a2f9cfbfe040
- https://git.kernel.org/stable/c/b287521e9e94bb342ebe5fd8c3fd7db9aef4e6f1
- https://git.kernel.org/stable/c/d34fb628f6ef522f996205a9e578216bbee09e84
- https://git.kernel.org/stable/c/e411df81cd862ef3d5b878120b2a2fef0ca9cdb1
