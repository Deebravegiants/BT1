# [M] CVE-2017-12190

## Summary
Severity: Medium
Advisory: CVE-2017-12190
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-11-22
Source: https://osv.dev/vulnerability/CVE-2017-12190
Type: osv

## Details
The bio_map_user_iov and bio_unmap_user functions in block/bio.c in the Linux kernel before 4.13.8 do unbalanced refcounting when a SCSI I/O vector has small consecutive buffers belonging to the same page. The bio_add_pc_page function merges them into one, but the page reference is never dropped. This causes a memory leak and possible system lockup (exploitable against the host OS by a guest OS user, if a SCSI disk is passed through to a virtual machine) due to an out-of-memory condition.

## References
- https://usn.ubuntu.com/3583-2/
- https://support.f5.com/csp/article/K93472064?utm_source=f5support&amp%3Butm_medium=RSS
- https://usn.ubuntu.com/3582-2/
- https://usn.ubuntu.com/3583-1/
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3582-1/
- https://access.redhat.com/errata/RHSA-2018:0654
- https://access.redhat.com/errata/RHSA-2018:1854
- https://access.redhat.com/errata/RHSA-2019:1170
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2019:1190
- http://seclists.org/oss-sec/2017/q4/52
- http://www.securityfocus.com/bid/101911
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.8
- https://bugzilla.redhat.com/show_bug.cgi?id=1495089
- https://github.com/torvalds/linux/commit/95d78c28b5a85bacbc29b8dba7c04babb9b0d467
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=2b04e8f6bbb196cab4b232af0f8d48ff2c7a8058
- https://github.com/torvalds/linux/commit/2b04e8f6bbb196cab4b232af0f8d48ff2c7a8058
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=95d78c28b5a85bacbc29b8dba7c04babb9b0d467
