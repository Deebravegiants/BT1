# [H] RDMA/hns: Fix Use-After-Free of rsv_qp on HIP08

## Summary
Severity: High
Advisory: CVE-2024-47750
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47750
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/hns: Fix Use-After-Free of rsv_qp on HIP08

Currently rsv_qp is freed before ib_unregister_device() is called
on HIP08. During the time interval, users can still dereg MR and
rsv_qp will be used in this process, leading to a UAF. Move the
release of rsv_qp after calling ib_unregister_device() to fix it.

## References
- https://git.kernel.org/stable/c/2ccf1c75d39949d8ea043d04a2e92d7100ea723d
- https://git.kernel.org/stable/c/60595923371c2ebe7faf82536c47eb0c967e3425
- https://git.kernel.org/stable/c/d2d9c5127122745da6e887f451dd248cfeffca33
- https://git.kernel.org/stable/c/dac2723d8bfa9cf5333f477741e6e5fa1ed34645
- https://git.kernel.org/stable/c/fd8489294dd2beefb70f12ec4f6132aeec61a4d0
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47750.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47750
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
