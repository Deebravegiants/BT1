# [M] CVE-2017-16818

## Summary
Severity: Medium
Advisory: CVE-2017-16818
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-12-20
Source: https://osv.dev/vulnerability/CVE-2017-16818
Type: osv

## Details
RADOS Gateway in Ceph 12.1.0 through 12.2.1 allows remote authenticated users to cause a denial of service (assertion failure and application exit) by leveraging "full" (not necessarily admin) privileges to post an invalid profile to the admin API, related to rgw/rgw_iam_policy.cc, rgw/rgw_basic_types.h, and rgw/rgw_iam_types.h.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U6VJA32U7HKGDRJQDJVM7JBYWD4T7BJL/
- https://bugzilla.redhat.com/show_bug.cgi?id=1515872
- https://github.com/ceph/ceph/commit/b3118cabb8060a8cc6a01c4e8264cb18e7b1745a
