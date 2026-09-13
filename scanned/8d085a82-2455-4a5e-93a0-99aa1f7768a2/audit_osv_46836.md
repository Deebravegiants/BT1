# [M] CVE-2015-5295

## Summary
Severity: Medium
Advisory: CVE-2015-5295
CVSS: 5.4 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2016-01-20
Source: https://osv.dev/vulnerability/CVE-2015-5295
Type: osv

## Details
The template-validate command in OpenStack Orchestration API (Heat) before 2015.1.3 (kilo) and 5.0.x before 5.0.1 (liberty) allows remote authenticated users to cause a denial of service (memory consumption) or determine the existence of local files via the resource type in a template, as demonstrated by file:///dev/zero.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176700.html
- http://rhn.redhat.com/errata/RHSA-2016-0266.html
- http://www.oracle.com/technetwork/topics/security/bulletinapr2016-2952098.html
- http://www.securityfocus.com/bid/81438
- https://bugs.launchpad.net/heat/+bug/1496277
- https://security.openstack.org/ossa/OSSA-2016-003.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176700.html
- https://bugs.launchpad.net/heat/+bug/1496277
