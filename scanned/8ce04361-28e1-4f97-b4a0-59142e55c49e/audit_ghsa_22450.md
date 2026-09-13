# [M] OpenStack Nova host data access through resize/migration

## Summary
Severity: Medium
Advisory: GHSA-49jv-37hm-6gfp
CVE: CVE-2016-2140
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-49jv-37hm-6gfp
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=12.0.0 <12.0.3

## Details
The libvirt driver in OpenStack Compute (Nova) before 2015.1.4 (kilo) and 12.0.x before 12.0.3 (liberty), when using raw storage and use_cow_images is set to false, allows remote authenticated users to read arbitrary files via a crafted qcow2 header in an ephemeral or root disk.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-2140
- https://github.com/openstack/nova/commit/0b194187db9da28225cb5e62be3b45aff5a1c793
- https://github.com/openstack/nova/commit/116b1210ab772c55d1ed1f715687d83877c92701
- https://github.com/openstack/nova/commit/f302bf04ab5dda89cf8ceaeed309006da90c0666
- https://access.redhat.com/errata/RHSA-2016:0363
- https://access.redhat.com/errata/RHSA-2016:0364
- https://access.redhat.com/errata/RHSA-2016:0365
- https://access.redhat.com/errata/RHSA-2016:0366
- https://access.redhat.com/security/cve/CVE-2016-2140
- https://bugs.launchpad.net/nova/+bug/1548450
- https://bugzilla.redhat.com/show_bug.cgi?id=1313454
- https://github.com/openstack/nova
- https://security.openstack.org/ossa/OSSA-2016-007.html
- http://seclists.org/oss-sec/2016/q1/563
- http://www.openwall.com/lists/oss-security/2016/03/08/6
- http://www.securityfocus.com/bid/84277
