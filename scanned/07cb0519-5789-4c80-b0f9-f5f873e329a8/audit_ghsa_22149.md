# [M] Openstack Neutron vulnerable to eavesdropping on private traffic

## Summary
Severity: Medium
Advisory: GHSA-8q95-jj7p-x93x
CVE: CVE-2018-14636
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8q95-jj7p-x93x
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=13.0.0.0b1 <13.0.0.0b2
- PyPI: `neutron` — affected >=12.0.0 <12.0.3
- PyPI: `neutron` — affected >=11.0.0 <11.0.5

## Details
Live-migrated instances are briefly able to inspect traffic for other instances on the same hypervisor. This brief window could be extended indefinitely if the instance's port is set administratively down prior to live-migration and kept down after the migration is complete. This is possible due to the Open vSwitch integration bridge being connected to the instance during migration. When connected to the integration bridge, all traffic for instances using the same Open vSwitch instance would potentially be visible to the migrated guest, as the required Open vSwitch VLAN filters are only applied post-migration. Versions of openstack-neutron before 13.0.0.0b2, 12.0.3, 11.0.5 are vulnerable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14636
- https://bugs.launchpad.net/neutron/+bug/1734320
- https://bugs.launchpad.net/neutron/+bug/1767422
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14636
- https://github.com/openstack/neutron
- https://github.com/pypa/advisory-database/tree/main/vulns/neutron/PYSEC-2018-94.yaml
