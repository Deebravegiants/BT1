# [M] CVE-2021-42739

## Summary
Severity: Medium
Advisory: CVE-2021-42739
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-20
Source: https://osv.dev/vulnerability/CVE-2021-42739
Type: osv

## Details
The firewire subsystem in the Linux kernel through 5.14.13 has a buffer overflow related to drivers/media/firewire/firedtv-avc.c and drivers/media/firewire/firedtv-ci.c, because avc_ca_pmt mishandles bounds checking.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=35d2969ea3c7d32aee78066b1f3cf61a0d935a4e
- https://lore.kernel.org/linux-media/YHaulytonFcW+lyZ%40mwanda/
- https://seclists.org/oss-sec/2021/q2/46
- https://www.starwindsoftware.com/security/sw-20220804-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=1951739
- https://www.oracle.com/security-alerts/cpujul2022.html
