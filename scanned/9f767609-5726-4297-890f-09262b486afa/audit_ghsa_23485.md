# [H] OpenStack TripleO Heat templates spoof metadata requests

## Summary
Severity: High
Advisory: GHSA-m94p-8942-pm49
CVE: CVE-2015-5303
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m94p-8942-pm49
Type: github-advisory

## Affected
- PyPI: `tripleo-heat-templates` — affected >=0 <0.8.10

## Details
The TripleO Heat templates (tripleo-heat-templates), when deployed via the commandline interface, allow remote attackers to spoof OpenStack Networking metadata requests by leveraging knowledge of the default value of the NeutronMetadataProxySharedSecret parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-5303
- https://github.com/openstack/tripleo-heat-templates/commit/1a0c7d97165c1b38dc9f78b82ac6ec8519fcf80c
- https://github.com/openstack/tripleo-heat-templates/commit/293f19b2a41386e1eea47a9e6add24b006c69c42
- https://access.redhat.com/errata/RHSA-2015:2650
- https://bugs.launchpad.net/tripleo/+bug/1516027
- https://github.com/openstack/tripleo-heat-templates
- https://github.com/pypa/advisory-database/tree/main/vulns/tripleo-heat-templates/PYSEC-2016-35.yaml
- https://opendev.org/openstack/tripleo-heat-templates/commit/1a0c7d97165c1b38dc9f78b82ac6ec8519fcf80c
- https://opendev.org/openstack/tripleo-heat-templates/commit/293f19b2a41386e1eea47a9e6add24b006c69c42
