# [M] CVE-2016-5009

## Summary
Severity: Medium
Advisory: CVE-2016-5009
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-07-12
Source: https://osv.dev/vulnerability/CVE-2016-5009
Type: osv

## Details
The handle_command function in mon/Monitor.cc in Ceph allows remote authenticated users to cause a denial of service (segmentation fault and ceph monitor crash) via an (1) empty or (2) crafted prefix.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00126.html
- http://tracker.ceph.com/issues/16297
- https://access.redhat.com/errata/RHSA-2016:1384
- https://access.redhat.com/errata/RHSA-2016:1385
- https://github.com/ceph/ceph/commit/957ece7e95d8f8746191fd9629622d4457d690d6
- https://github.com/ceph/ceph/pull/9700
