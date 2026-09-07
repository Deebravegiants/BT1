# [M] OpenStack Compute (Nova) Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-43hc-pwvx-pmfg
CVE: CVE-2014-3708
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-43hc-pwvx-pmfg
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <2014.1.4
- PyPI: `nova` — affected >=2014.2.0 <2014.2.1

## Details
OpenStack Compute (Nova) before 2014.1.4 and 2014.2.x before 2014.2.1 allows remote authenticated users to cause a denial of service (CPU consumption) via an IP filter in a list active servers API request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3708
- https://access.redhat.com/errata/RHSA-2015:0843
- https://access.redhat.com/errata/RHSA-2015:0844
- https://access.redhat.com/security/cve/CVE-2014-3708
- https://bugs.launchpad.net/nova/+bug/1358583
- https://bugzilla.redhat.com/show_bug.cgi?id=1154951
- https://opendev.org/openstack/nova
- https://web.archive.org/web/20200901000000*/http://www.securityfocus.com/bid/70777
- http://lists.openstack.org/pipermail/openstack-announce/2014-October/000301.html
- http://rhn.redhat.com/errata/RHSA-2015-0843.html
- http://rhn.redhat.com/errata/RHSA-2015-0844.html
- http://www.securityfocus.com/bid/70777
