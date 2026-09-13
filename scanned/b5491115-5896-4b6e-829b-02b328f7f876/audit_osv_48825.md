# [M] CVE-2018-14656

## Summary
Severity: Medium
Advisory: CVE-2018-14656
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-10-08
Source: https://osv.dev/vulnerability/CVE-2018-14656
Type: osv

## Details
A missing address check in the callers of the show_opcodes() in the Linux kernel allows an attacker to dump the kernel memory at an arbitrary kernel address into the dmesg log.

## References
- https://lore.kernel.org/lkml/20180828154901.112726-1-jannh%40google.com/T/
- http://www.securitytracker.com/id/1041804
- https://seclists.org/oss-sec/2018/q4/9
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1650
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14656
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=342db04ae71273322f0011384a9ed414df8bdae4
