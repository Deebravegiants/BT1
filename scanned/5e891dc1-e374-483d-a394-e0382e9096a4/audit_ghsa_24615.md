# [H] OpenStack Ironic Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: High
Advisory: GHSA-f7cr-7c2c-fm8r
CVE: CVE-2016-4985
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-f7cr-7c2c-fm8r
Type: github-advisory

## Affected
- PyPI: `ironic` — affected >=0 <4.2.5
- PyPI: `ironic` — affected >=5.0 <5.1.2

## Details
The ironic-api service in OpenStack Ironic before 4.2.5 (Liberty) and 5.x before 5.1.2 (Mitaka) allows remote attackers to obtain sensitive information about a registered node by leveraging knowledge of the MAC address of a network card belonging to that node and sending a crafted POST request to the `v1/drivers/$DRIVER_NAME/vendor_passthru` resource.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4985
- https://github.com/openstack/ironic/commit/426a306fb580762e97ada04e1253dedd9b64d410
- https://github.com/openstack/ironic/commit/affec224977174581d19a2b914772cb0409f633e
- https://github.com/openstack/ironic/commit/f5a3ff1dfcde068769f9a2a477ba6a9edaf69c77
- https://access.redhat.com/errata/RHSA-2016:1377
- https://access.redhat.com/errata/RHSA-2016:1378
- https://access.redhat.com/security/cve/CVE-2016-4985
- https://bugs.launchpad.net/ironic/+bug/1572796
- https://bugzilla.redhat.com/show_bug.cgi?id=1346193
- https://github.com/openstack/ironic
- https://review.openstack.org/332195
- https://review.openstack.org/332196
- https://review.openstack.org/332197
- http://www.openwall.com/lists/oss-security/2016/06/21/6
