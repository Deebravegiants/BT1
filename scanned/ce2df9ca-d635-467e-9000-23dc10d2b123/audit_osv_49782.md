# [M] CVE-2019-19058

## Summary
Severity: Medium
Advisory: CVE-2019-19058
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19058
Type: osv

## Details
A memory leak in the alloc_sgtable() function in drivers/net/wireless/intel/iwlwifi/fw/dbg.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering alloc_page() failures, aka CID-b4b814fec1a5.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4300-1/
- https://usn.ubuntu.com/4301-1/
- https://usn.ubuntu.com/4302-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://github.com/torvalds/linux/commit/b4b814fec1a5a849383f7b3886b654a13abbda7d
