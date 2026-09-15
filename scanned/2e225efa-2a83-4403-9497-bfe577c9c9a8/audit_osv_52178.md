# [M] CVE-2021-47166

## Summary
Severity: Medium
Advisory: CVE-2021-47166
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47166
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Don't corrupt the value of pg_bytes_written in nfs_do_recoalesce()

The value of mirror->pg_bytes_written should only be updated after a
successful attempt to flush out the requests on the list.

## References
- https://git.kernel.org/stable/c/7087db95c0a06ab201b8ebfac6a7ec1e34257997
- https://git.kernel.org/stable/c/785917316b25685c9b3a2a88f933139f2de75e33
- https://git.kernel.org/stable/c/b291baae24f876acd5a5dd57d0bb2bbac8a68b0c
- https://git.kernel.org/stable/c/c757c1f1e65d89429db1409429436cf40d47c008
- https://git.kernel.org/stable/c/e8b8418ce14ae66ee55179901edd12191ab06a9e
- https://git.kernel.org/stable/c/0d0ea309357dea0d85a82815f02157eb7fcda39f
- https://git.kernel.org/stable/c/2fe1cac336b55a1f79e603e9ce3552c3623e90eb
- https://git.kernel.org/stable/c/40f139a6d50c232c0d1fd1c5e65a845c62db0ede
