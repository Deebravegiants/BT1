# [C] NFSv4.2: Rework scratch handling for READ_PLUS (again)

## Summary
Severity: Critical
Advisory: CVE-2023-53360
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53360
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4.2: Rework scratch handling for READ_PLUS (again)

I found that the read code might send multiple requests using the same
nfs_pgio_header, but nfs4_proc_read_setup() is only called once. This is
how we ended up occasionally double-freeing the scratch buffer, but also
means we set a NULL pointer but non-zero length to the xdr scratch
buffer. This results in an oops the first time decoding needs to copy
something to scratch, which frequently happens when decoding READ_PLUS
hole segments.

I fix this by moving scratch handling into the pageio read code. I
provide a function to allocate scratch space for decoding read replies,
and free the scratch buffer when the nfs_pgio_header is freed.

## References
- https://git.kernel.org/stable/c/303a78052091c81e9003915c521fdca1c7e117af
- https://git.kernel.org/stable/c/a2f4cb206bd94b3f4a7bb05fcdce9525283b5681
- https://git.kernel.org/stable/c/adac9f0ddd2b291c7ce41f549fdb27a13616cff5
- https://git.kernel.org/stable/c/ae5d5672f1db711e91db6f52df5cb16ecd8f5692
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53360.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53360
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
