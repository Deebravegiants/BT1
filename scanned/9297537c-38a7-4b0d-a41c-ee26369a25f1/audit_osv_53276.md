# [M] CVE-2022-3594

## Summary
Severity: Medium
Advisory: CVE-2022-3594
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-10-18
Source: https://osv.dev/vulnerability/CVE-2022-3594
Type: osv

## Details
A vulnerability was found in Linux Kernel. It has been declared as problematic. Affected by this vulnerability is the function intr_callback of the file drivers/net/usb/r8152.c of the component BPF. The manipulation leads to logging of excessive data. The attack can be launched remotely. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-211363.

## References
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
- https://vuldb.com/?id.211363
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf-next.git/commit/?id=93e2be344a7db169b7119de21ac1bf253b8c6907
