# [H] CVE-2021-46952

## Summary
Severity: High
Advisory: CVE-2021-46952
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2021-46952
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: fs_context: validate UDP retrans to prevent shift out-of-bounds

Fix shift out-of-bounds in xprt_calc_majortimeo(). This is caused
by a garbage timeout (retrans) mount option being passed to nfs mount,
in this case from syzkaller.

If the protocol is XPRT_TRANSPORT_UDP, then 'retrans' is a shift
value for a 64-bit long integer, so 'retrans' cannot be >= 64.
If it is >= 64, fail the mount and return an error.

## References
- https://git.kernel.org/stable/c/2f3380121d49e829fb73ba86240c181bc32ad897
- https://git.kernel.org/stable/c/3d0163821c035040a46d816a42c0780f0f0a30a8
- https://git.kernel.org/stable/c/96fa26b74cdcf9f5c98996bf36bec9fb5b19ffe2
- https://git.kernel.org/stable/c/c09f11ef35955785f92369e25819bf0629df2e59
