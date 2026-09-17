# [M] CVE-2022-38096

## Summary
Severity: Medium
Advisory: CVE-2022-38096
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-09
Source: https://osv.dev/vulnerability/CVE-2022-38096
Type: osv

## Details
A NULL pointer dereference vulnerability was found in vmwgfx driver in drivers/gpu/vmxgfx/vmxgfx_execbuf.c in GPU component of Linux kernel with device file '/dev/dri/renderD128 (or Dxxx)'. This flaw allows a local attacker with a user account on the system to gain privilege, causing a denial of service(DoS).

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://bugzilla.openanolis.cn/show_bug.cgi?id=2073
