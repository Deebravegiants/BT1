# [M] OpenStack Keystone and other components vulnerable to Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-qh2x-hpf9-cf2g
CVE: CVE-2013-2255
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-05
Source: https://github.com/advisories/GHSA-qh2x-hpf9-cf2g
Type: github-advisory

## Affected
- PyPI: `python-keystoneclient` — affected >=0 <0.4.0
- PyPI: `cinder` — affected >=0 <7.0.0a0
- PyPI: `neutron` — affected >=0 <7.0.0a0
- PyPI: `keystone` — affected >=0 <8.0.0a0

## Details
HTTPSConnections in OpenStack Keystone 2013, OpenStack Compute 2013.1, and possibly other OpenStack components, fail to validate server-side SSL certificates.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-2255
- https://github.com/openstack/cinder/commit/0f9652d92e175a1f7dc3c2a37ab444b8f189375a
- https://github.com/openstack/keystone/commit/5bd4c2984d329625a2a8442b316fa235dbb88a3d
- https://github.com/openstack/neutron/commit/7255e056092f034daaeb4246a812900645d46911
- https://github.com/openstack/python-keystoneclient/commit/20e166fd8a943ee3f91ba362a47e9c14c7cc5f4c
- https://access.redhat.com/security/cve/cve-2013-2255
- https://bugs.launchpad.net/ossn/+bug/1188189
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2013-2255
- https://bugzilla.suse.com/show_bug.cgi?id=CVE-2013-2255
- https://exchange.xforce.ibmcloud.com/vulnerabilities/85562
- https://security-tracker.debian.org/tracker/CVE-2013-2255
- https://web.archive.org/web/20200229073508/https://www.securityfocus.com/bid/61118
