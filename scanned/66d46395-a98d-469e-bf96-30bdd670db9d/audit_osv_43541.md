# [C] RDMA/siw: Fix endpoint/socket association handling

## Summary
Severity: Critical
Advisory: CVE-2026-74345
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74345
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/siw: Fix endpoint/socket association handling

Disassociating a socket from an endpoint via siw_socket_disassoc() may
release the last reference on that endpoint and free it. Therefore, don't
clear the endpoints socket pointer after calling that function, but
within.

This fixes a:

  BUG: KASAN: slab-use-after-free in siw_cm_work_handler (drivers/infiniband/sw/siw/siw_cm.c:1053 drivers/infiniband/sw/siw/siw_cm.c:1075)

which occurred after processing a malformed MPA request during connection
establishment, causing the new endpoint to be closed.

## References
- https://git.kernel.org/stable/c/b28d513393f81e2de00f82970487a9d001557e4e
- https://git.kernel.org/stable/c/b6cf763eee0a932792bef64ceaca568d324192fc
- https://git.kernel.org/stable/c/ea4f6f6c53577fb3f05dbd78b15e586772d49831
- https://git.kernel.org/stable/c/f6183983ce1ff254d629a333739082b39d7c5eb6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74345.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74345
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
