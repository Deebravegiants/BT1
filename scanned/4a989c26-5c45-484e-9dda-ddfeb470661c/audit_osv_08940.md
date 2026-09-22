# [H] CVE-2016-7031

## Summary
Severity: High
Advisory: CVE-2016-7031
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-7031
Type: osv

## Details
The RGW code in Ceph before 10.0.1, when authenticated-read ACL is applied to a bucket, allows remote attackers to list the bucket contents via a URL.

## References
- http://www.securityfocus.com/bid/93240
- http://docs.ceph.com/docs/master/release-notes/#v10-0-1
- http://rhn.redhat.com/errata/RHSA-2016-1972.html
- http://rhn.redhat.com/errata/RHSA-2016-1973.html
- http://tracker.ceph.com/issues/13207
- https://github.com/ceph/ceph/pull/6057
