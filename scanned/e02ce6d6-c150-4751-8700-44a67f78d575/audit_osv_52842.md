# [H] CVE-2022-1679

## Summary
Severity: High
Advisory: CVE-2022-1679
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-16
Source: https://osv.dev/vulnerability/CVE-2022-1679
Type: osv

## Details
A use-after-free flaw was found in the Linux kernel’s Atheros wireless adapter driver in the way a user forces the ath9k_htc_wait_for_target function to fail with some input messages. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://security.netapp.com/advisory/ntap-20220629-0007/
- https://lists.debian.org/debian-lts-announce/2022/10/msg00000.html
- https://lore.kernel.org/lkml/87ilqc7jv9.fsf%40kernel.org/t/
