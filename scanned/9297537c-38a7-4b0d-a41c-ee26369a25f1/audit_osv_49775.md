# [M] CVE-2019-19046

## Summary
Severity: Medium
Advisory: CVE-2019-19046
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19046
Type: osv

## Details
A memory leak in the __ipmi_bmc_register() function in drivers/char/ipmi/ipmi_msghandler.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering ida_simple_get() failure, aka CID-4aa7afb0ee20. NOTE: third parties dispute the relevance of this because an attacker cannot realistically control this failure at probe time

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://usn.ubuntu.com/4302-1/
- https://usn.ubuntu.com/4319-1/
- https://usn.ubuntu.com/4325-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://bugzilla.suse.com/show_bug.cgi?id=1157304
- https://github.com/torvalds/linux/commit/4aa7afb0ee20a97fbf0c5bab3df028d5fb85fdab
