# [M] OpenStack Neutron can use an incorrect ID during policy enforcement

## Summary
Severity: Medium
Advisory: GHSA-f27h-g923-68hw
CVE: CVE-2024-53916
CWE: CWE-345, CWE-754
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-f27h-g923-68hw
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=23.0.0 <23.2.1
- PyPI: `neutron` — affected >=24.0.0 <24.0.2
- PyPI: `neutron` — affected >=25.0.0 <25.0.1

## Details
In OpenStack Neutron before 25.0.1, neutron/extensions/tagging.py can use an incorrect ID during policy enforcement. It does not apply the proper policy check for changing network tags. An unprivileged tenant is able to change (add and clear) tags on network objects that do not belong to the tenant, and this action is not subjected to the proper policy authorization check. This affects 23 before 23.2.1, 24 before 24.0.2, and 25 before 25.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53916
- https://github.com/openstack/neutron
- https://github.com/openstack/neutron/blob/363ffa6e9e1ab5968f87d45bc2f1cb6394f48b9f/neutron/extensions/tagging.py#L138-L232
- https://review.opendev.org/c/openstack/neutron/+/935883
- https://review.opendev.org/q/project:openstack/neutron
- https://security.openstack.org/ossa/OSSA-2024-005.html
- http://www.openwall.com/lists/oss-security/2024/12/03/1
