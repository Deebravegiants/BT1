# [M] CVE-2023-4459

## Summary
Severity: Medium
Advisory: CVE-2023-4459
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-21
Source: https://osv.dev/vulnerability/CVE-2023-4459
Type: osv

## Details
A NULL pointer dereference flaw was found in vmxnet3_rq_cleanup in drivers/net/vmxnet3/vmxnet3_drv.c in the networking sub-component in vmxnet3 in the Linux Kernel. This issue may allow a local attacker with normal user privilege to cause a denial of service due to a missing sanity check during cleanup.

## References
- https://access.redhat.com/errata/RHSA-2024:0412
- https://access.redhat.com/errata/RHSA-2024:1250
- https://access.redhat.com/errata/RHSA-2024:1382
- https://access.redhat.com/errata/RHSA-2024:2008
- https://access.redhat.com/errata/RHSA-2024:1306
- https://access.redhat.com/errata/RHSA-2024:1367
- https://access.redhat.com/errata/RHSA-2024:2006
- https://access.redhat.com/security/cve/CVE-2023-4459
- https://bugzilla.redhat.com/show_bug.cgi?id=2219268
- https://github.com/torvalds/linux/commit/edf410cb74dc612fd47ef5be319c5a0bcd6e6ccd
