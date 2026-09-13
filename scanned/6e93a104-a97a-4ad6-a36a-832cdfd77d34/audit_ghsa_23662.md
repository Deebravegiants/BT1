# [M] OpenStack Compute (nova) allows remote authenticated users to cause a denial of service

## Summary
Severity: Medium
Advisory: GHSA-mfmj-gwg3-vhw7
CVE: CVE-2015-3280
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mfmj-gwg3-vhw7
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <2014.2.4
- PyPI: `nova` — affected >=2015.1.0 <2015.1.2

## Details
OpenStack Compute (nova) before 2014.2.4 (juno) and 2015.1.x before 2015.1.2 (kilo) does not properly delete instances from compute nodes, which allows remote authenticated users to cause a denial of service (disk consumption) by deleting instances while in the resize state.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3280
- https://access.redhat.com/errata/RHSA-2015:1898
- https://access.redhat.com/security/cve/CVE-2015-3280
- https://bugzilla.redhat.com/show_bug.cgi?id=1257942
- https://launchpad.net/bugs/1392527
- https://opendev.org/openstack/nova
- https://security.openstack.org/ossa/OSSA-2015-017.html
- https://web.archive.org/web/20200228023247/http://www.securityfocus.com/bid/76553
- http://rhn.redhat.com/errata/RHSA-2015-1898.html
- http://www.oracle.com/technetwork/topics/security/bulletinjan2016-2867206.html
- http://www.securityfocus.com/bid/76553
