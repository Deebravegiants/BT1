# [H] CVE-2018-10861

## Summary
Severity: High
Advisory: CVE-2018-10861
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2018-07-10
Source: https://osv.dev/vulnerability/CVE-2018-10861
Type: osv

## Details
A flaw was found in the way ceph mon handles user requests. Any authenticated ceph user having read access to ceph can delete, create ceph storage pools and corrupt snapshot images. Ceph branches master, mimic, luminous and jewel are believed to be affected.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00100.html
- http://www.securityfocus.com/bid/104742
- https://access.redhat.com/errata/RHSA-2018:2177
- https://access.redhat.com/errata/RHSA-2018:2179
- https://access.redhat.com/errata/RHSA-2018:2261
- https://access.redhat.com/errata/RHSA-2018:2274
- https://www.debian.org/security/2018/dsa-4339
- http://tracker.ceph.com/issues/24838
- https://bugzilla.redhat.com/show_bug.cgi?id=1593308
- https://github.com/ceph/ceph/commit/975528f632f73fbffa3f1fee304e3bbe3296cffc
