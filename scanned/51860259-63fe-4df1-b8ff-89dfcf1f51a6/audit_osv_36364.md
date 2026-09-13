# [H] fbdev: smscufx: properly copy ioctl memory to kernelspace

## Summary
Severity: High
Advisory: CVE-2026-23236
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-23236
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.10.251, >=5.11.0 <5.15.201, >=5.16.0 <6.1.164, >=6.2.0 <6.6.127, >=6.7.0 <6.12.74, >=6.13.0 <6.18.13, >=6.19.0 <6.19.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

fbdev: smscufx: properly copy ioctl memory to kernelspace

The UFX_IOCTL_REPORT_DAMAGE ioctl does not properly copy data from
userspace to kernelspace, and instead directly references the memory,
which can cause problems if invalid data is passed from userspace.  Fix
this all up by correctly copying the memory before accessing it within
the kernel.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/061cfeb560aa3ddc174153dbe5be9d0b55eb7248
- https://git.kernel.org/stable/c/0634e8d650993602fc5b389ff7ac525f6542e141
- https://git.kernel.org/stable/c/120adae7b42faa641179270c067864544a50ab69
- https://git.kernel.org/stable/c/1c008ad0f0d1c1523902b9cdb08e404129677bfc
- https://git.kernel.org/stable/c/52917e265aa5f848212f60fc50fc504d8ef12866
- https://git.kernel.org/stable/c/6167af934f956d3ae1e06d61f45cd0d1004bbe1a
- https://git.kernel.org/stable/c/a0321e6e58facb39fe191caa0e52ed9aab6a48fe
- https://git.kernel.org/stable/c/f1e91bd4efeae48b0f42caed7e8ce2e3a0d05b02
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23236.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23236
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
