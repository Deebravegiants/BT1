# [H] CVE-2022-1050

## Summary
Severity: High
Advisory: CVE-2022-1050
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-03-29
Source: https://osv.dev/vulnerability/CVE-2022-1050
Type: osv

## Details
A flaw was found in the QEMU implementation of VMWare's paravirtual RDMA device. This flaw allows a crafted guest driver to execute HW commands when shared buffers are not yet allocated, potentially leading to a use-after-free condition.

## References
- https://lists.debian.org/debian-lts-announce/2023/03/msg00013.html
- https://bugzilla.redhat.com/show_bug.cgi?id=2069625
