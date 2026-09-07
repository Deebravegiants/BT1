# [M] OpenStack Compute (Nova) has Insufficient Verification of Data Authenticity

## Summary
Severity: Medium
Advisory: GHSA-x8xr-rm9r-7mvf
CVE: CVE-2015-0259
CWE: CWE-345
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-x8xr-rm9r-7mvf
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <2014.1.4
- PyPI: `nova` — affected >=2014.2.0 <2014.2.3

## Details
OpenStack Compute (Nova) before 2014.1.4, 2014.2.x before 2014.2.3, and kilo before kilo-3 does not validate the origin of websocket requests, which allows remote attackers to hijack the authentication of users for access to consoles via a crafted webpage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-0259
- https://access.redhat.com/errata/RHSA-2015:0790
- https://access.redhat.com/errata/RHSA-2015:0843
- https://access.redhat.com/errata/RHSA-2015:0844
- https://access.redhat.com/security/cve/CVE-2015-0259
- https://bugs.launchpad.net/nova/+bug/1409142
- https://bugzilla.redhat.com/show_bug.cgi?id=1190112
- https://opendev.org/openstack/nova
- http://lists.openstack.org/pipermail/openstack-announce/2015-March/000341.html
- http://rhn.redhat.com/errata/RHSA-2015-0790.html
- http://rhn.redhat.com/errata/RHSA-2015-0843.html
- http://rhn.redhat.com/errata/RHSA-2015-0844.html
