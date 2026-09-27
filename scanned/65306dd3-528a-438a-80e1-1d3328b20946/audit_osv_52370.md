# [C] CVE-2021-47378

## Summary
Severity: Critical
Advisory: CVE-2021-47378
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47378
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-rdma: destroy cm id before destroy qp to avoid use after free

We should always destroy cm_id before destroy qp to avoid to get cma
event after qp was destroyed, which may lead to use after free.
In RDMA connection establishment error flow, don't destroy qp in cm
event handler.Just report cm_error to upper level, qp will be destroy
in nvme_rdma_alloc_queue() after destroy cm id.

## References
- https://git.kernel.org/stable/c/9817d763dbe15327b9b3ff4404fa6f27f927e744
- https://git.kernel.org/stable/c/d268a182c56e8361e19fb781137411643312b994
- https://git.kernel.org/stable/c/ecf0dc5a904830c926a64feffd8e01141f89822f
