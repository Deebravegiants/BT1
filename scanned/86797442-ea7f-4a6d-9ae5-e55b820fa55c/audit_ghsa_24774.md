# [M] OpenStack Neutron Improper Input Validation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wf44-4mgj-rwvx
CVE: CVE-2015-3221
CWE: CWE-20
Ecosystem: PyPI
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-wf44-4mgj-rwvx
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=2000 <2014.2.4
- PyPI: `neutron` — affected >=2015.1.0 <2015.1.1

## Details
OpenStack Neutron before 2014.2.4 (juno) and 2015.1.x before 2015.1.1 (kilo), when using the IPTables firewall driver, allows remote authenticated users to cause a denial of service (L2 agent crash) by adding an address pair that is rejected by the ipset tool.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3221
- https://access.redhat.com/errata/RHSA-2015:1680
- https://access.redhat.com/security/cve/CVE-2015-3221
- https://bugs.launchpad.net/neutron/+bug/1461054
- https://bugzilla.redhat.com/show_bug.cgi?id=1232284
- https://git.openstack.org/cgit/openstack/neutron/commit/?id=9ff6138c47c95034ba845e9448ddffd147b51f38
- https://github.com/pypa/advisory-database/tree/main/vulns/neutron/PYSEC-2026-856.yaml
- https://opendev.org/openstack/neutron
- https://web.archive.org/web/20200228084753/http://www.securityfocus.com/bid/75368
- http://lists.openstack.org/pipermail/openstack-announce/2015-June/000377.html
- http://rhn.redhat.com/errata/RHSA-2015-1680.html
