# [H] CVE-2023-4387

## Summary
Severity: High
Advisory: CVE-2023-4387
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2023-08-16
Source: https://osv.dev/vulnerability/CVE-2023-4387
Type: osv

## Details
A use-after-free flaw was found in vmxnet3_rq_alloc_rx_buf in drivers/net/vmxnet3/vmxnet3_drv.c in VMware's vmxnet3 ethernet NIC driver in the Linux Kernel. This issue could allow a local attacker to crash the system due to a double-free while cleaning up vmxnet3_rq_cleanup_all, which could also lead to a kernel information leak problem.

## References
- https://access.redhat.com/security/cve/CVE-2023-4387
- https://access.redhat.com/errata/RHSA-2022:7683
- https://access.redhat.com/errata/RHSA-2022:8267
- https://bugzilla.redhat.com/show_bug.cgi?id=2219270
- https://github.com/torvalds/linux/commit/9e7fef9521e73ca8afd7da9e58c14654b02dfad8
