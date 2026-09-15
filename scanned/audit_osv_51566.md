# [H] CVE-2021-3348

## Summary
Severity: High
Advisory: CVE-2021-3348
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-01
Source: https://osv.dev/vulnerability/CVE-2021-3348
Type: osv

## Details
nbd_add_socket in drivers/block/nbd.c in the Linux kernel through 5.10.12 has an ndb_queue_rq use-after-free that could be triggered by local attackers (with access to the nbd device) via an I/O request at a certain point during device setup, aka CID-b98e762e3d71.

## References
- https://lists.debian.org/debian-lts-announce/2021/03/msg00035.html
- http://www.openwall.com/lists/oss-security/2021/02/01/1
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=b98e762e3d71e893b221f871825dc64694cfb258
- https://www.openwall.com/lists/oss-security/2021/01/28/3
