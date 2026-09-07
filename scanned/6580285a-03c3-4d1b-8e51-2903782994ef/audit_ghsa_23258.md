# [M] OpenStack Nova Router metadata queries are not restricted by tenant

## Summary
Severity: Medium
Advisory: GHSA-22w9-j288-8p9w
CVE: CVE-2013-6419
CWE: CWE-200
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-22w9-j288-8p9w
Type: github-advisory

## Affected
- PyPI: `nova` — affected >=0 <12.0.0a0

## Details
Interaction error in OpenStack Nova and Neutron before Havana 2013.2.1 and icehouse-1 does not validate the instance ID of the tenant making a request, which allows remote tenants to obtain sensitive metadata by spoofing the device ID that is bound to a port, which is not properly handled by (1) api/metadata/handler.py in Nova and (2) the neutron-metadata-agent (`agent/metadata/agent.py`) in Neutron.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6419
- https://github.com/openstack/nova/commit/07006be9165d1008ca0382b6f0ad25b13a676a55
- https://github.com/openstack/nova/commit/af2f823107010933ecd94a9c938f8b739baaecb7
- https://github.com/openstack/nova/commit/bce36e9bdb1fcb9658f7b684d160e656e88d816c
- https://bugs.launchpad.net/neutron/+bug/1235450
- https://github.com/openstack/nova
- https://review.openstack.org/#/c/61428/2/nova/api/metadata/handler.py
- https://review.openstack.org/#/c/61439/1/neutron/agent/metadata/agent.py
- http://rhn.redhat.com/errata/RHSA-2014-0091.html
- http://rhn.redhat.com/errata/RHSA-2014-0231.html
- http://www.openwall.com/lists/oss-security/2013/12/11/8
- http://www.securityfocus.com/bid/64250
