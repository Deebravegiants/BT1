# [M] OpenStack Compute (Nova) allows remote attackers to bypass intended restriction

## Summary
Severity: Medium
Advisory: GHSA-67rh-9p29-vrxr
CVE: CVE-2015-7713
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-67rh-9p29-vrxr
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <2014.2.4
- PyPI: `nova` — affected >=2015.1.0 <2015.1.2

## Details
OpenStack Compute (Nova) before 2014.2.4 (juno) and 2015.1.x before 2015.1.2 (kilo) do not properly apply security group changes, which allows remote attackers to bypass intended restriction by leveraging an instance that was running when the change was made.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7713
- https://access.redhat.com/errata/RHSA-2015:2673
- https://access.redhat.com/errata/RHSA-2015:2684
- https://access.redhat.com/errata/RHSA-2016:0013
- https://access.redhat.com/errata/RHSA-2016:0017
- https://access.redhat.com/security/cve/CVE-2015-7713
- https://bugs.launchpad.net/nova/+bug/1491307
- https://bugs.launchpad.net/nova/+bug/1492961
- https://bugzilla.redhat.com/show_bug.cgi?id=1269119
- https://opendev.org/openstack/nova
- https://security.openstack.org/ossa/OSSA-2015-021.html
- https://web.archive.org/web/20200228024902/http://www.securityfocus.com/bid/76960
- http://rhn.redhat.com/errata/RHSA-2015-2684.html
- http://www.securityfocus.com/bid/76960
