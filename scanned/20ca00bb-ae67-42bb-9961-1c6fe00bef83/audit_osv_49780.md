# [M] CVE-2019-19055

## Summary
Severity: Medium
Advisory: CVE-2019-19055
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19055
Type: osv

## Details
A memory leak in the nl80211_get_ftm_responder_stats() function in net/wireless/nl80211.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering nl80211hdr_put() failures, aka CID-1399c59fa929. NOTE: third parties dispute the relevance of this because it occurs on a code path where a successful allocation has already occurred

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://usn.ubuntu.com/4225-1/
- https://usn.ubuntu.com/4225-2/
- https://usn.ubuntu.com/4226-1/
- https://bugzilla.suse.com/show_bug.cgi?id=1157319
- https://github.com/torvalds/linux/commit/1399c59fa92984836db90538cf92397fe7caaa57
