# [H] io_uring/eventfd: ensure io_eventfd_signal() defers another RCU period

## Summary
Severity: High
Advisory: CVE-2025-21655
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-20
Source: https://osv.dev/vulnerability/CVE-2025-21655
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/eventfd: ensure io_eventfd_signal() defers another RCU period

io_eventfd_do_signal() is invoked from an RCU callback, but when
dropping the reference to the io_ev_fd, it calls io_eventfd_free()
directly if the refcount drops to zero. This isn't correct, as any
potential freeing of the io_ev_fd should be deferred another RCU grace
period.

Just call io_eventfd_put() rather than open-code the dec-and-test and
free, which will correctly defer it another RCU grace period.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/6b63308c28987c6010b1180c72a6db4df6c68033
- https://git.kernel.org/stable/c/8efff2aa2d95dc437ab67c5b4a9f1d3f367baa10
- https://git.kernel.org/stable/c/a7085c3ae43b86d4b3d1b8275e6a67f14257e3b7
- https://git.kernel.org/stable/c/c9a40292a44e78f71258b8522655bffaf5753bdb
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://project-zero.issues.chromium.org/issues/388499293
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21655.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21655
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
