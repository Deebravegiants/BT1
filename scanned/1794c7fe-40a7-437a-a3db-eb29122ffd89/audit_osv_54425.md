# [M] CVE-2023-6121

## Summary
Severity: Medium
Advisory: CVE-2023-6121
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-11-16
Source: https://osv.dev/vulnerability/CVE-2023-6121
Type: osv

## Details
An out-of-bounds read vulnerability was found in the NVMe-oF/TCP subsystem in the Linux kernel. This issue may allow a remote attacker to send a crafted TCP packet, triggering a heap-based buffer overflow that results in kmalloc data being printed and potentially leaked to the kernel ring buffer (dmesg).

## References
- https://lists.debian.org/debian-lts-announce/2024/01/msg00005.html
- https://access.redhat.com/errata/RHSA-2024:2394
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-6121
- https://bugzilla.redhat.com/show_bug.cgi?id=2250043
