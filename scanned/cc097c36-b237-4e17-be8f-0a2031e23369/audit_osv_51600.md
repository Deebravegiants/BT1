# [H] CVE-2021-3491

## Summary
Severity: High
Advisory: CVE-2021-3491
Aliases: A-190877100, PUB-A-190877100
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2021-06-04
Source: https://osv.dev/vulnerability/CVE-2021-3491
Type: osv

## Details
The io_uring subsystem in the Linux kernel allowed the MAX_RW_COUNT limit to be bypassed in the PROVIDE_BUFFERS operation, which led to negative values being usedin mem_rw when reading /proc/<PID>/mem. This could be used to create a heap overflow leading to arbitrary code execution in the kernel. It was addressed via commit d1f82808877b ("io_uring: truncate lengths larger than MAX_RW_COUNT on provide buffers") (v5.13-rc1) and backported to the stable kernels in v5.12.4, v5.11.21, and v5.10.37. It was introduced in ddf0322db79c ("io_uring: add IORING_OP_PROVIDE_BUFFERS") (v5.7-rc1).

## References
- https://ubuntu.com/security/notices/USN-4949-1
- https://ubuntu.com/security/notices/USN-4950-1
- https://www.zerodayinitiative.com/advisories/ZDI-21-589/
- https://security.netapp.com/advisory/ntap-20210716-0004/
- https://www.openwall.com/lists/oss-security/2021/05/11/13
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=d1f82808877bb10d3deee7cf3374a4eb3fb582db
