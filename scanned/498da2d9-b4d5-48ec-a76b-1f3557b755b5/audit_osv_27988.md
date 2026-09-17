# [H] scsi: qla2xxx: Fix double free of the ha->vp_map pointer

## Summary
Severity: High
Advisory: CVE-2024-26930
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26930
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.24, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: qla2xxx: Fix double free of the ha->vp_map pointer

Coverity scan reported potential risk of double free of the pointer
ha->vp_map.  ha->vp_map was freed in qla2x00_mem_alloc(), and again freed
in function qla2x00_mem_free(ha).

Assign NULL to vp_map and kfree take care of NULL.

## References
- https://git.kernel.org/stable/c/825d63164a2e6bacb059a9afb5605425b485413f
- https://git.kernel.org/stable/c/b7deb675d674f44e0ddbab87fee8f9f098925e73
- https://git.kernel.org/stable/c/e288285d47784fdcf7c81be56df7d65c6f10c58b
- https://git.kernel.org/stable/c/f14cee7a882cb79528f17a2335f53e9fd1848467
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26930.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26930
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
