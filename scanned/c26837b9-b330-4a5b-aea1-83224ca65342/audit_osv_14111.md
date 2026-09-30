# [H] CVE-2018-7262

## Summary
Severity: High
Advisory: CVE-2018-7262
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-19
Source: https://osv.dev/vulnerability/CVE-2018-7262
Type: osv

## Details
In Ceph before 12.2.3 and 13.x through 13.0.1, the rgw_civetweb.cc RGWCivetWeb::init_env function in radosgw doesn't handle malformed HTTP headers properly, allowing for denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/74VI6EPZ6LD2O4JJXJBTYQ4U4VUO2ZDO/
- https://access.redhat.com/errata/RHSA-2018:0546
- https://access.redhat.com/errata/RHSA-2018:0548
- http://tracker.ceph.com/issues/23039
- https://bugzilla.redhat.com/show_bug.cgi?id=1546611
- https://github.com/ceph/ceph/pull/20488
