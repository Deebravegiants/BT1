# [M]  OpenStack improperly deletes access rules

## Summary
Severity: Medium
Advisory: GHSA-2ppf-2m6f-6v6f
CVE: CVE-2023-6110
CWE: CWE-237
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-11-17
Source: https://github.com/advisories/GHSA-2ppf-2m6f-6v6f
Type: github-advisory

## Affected
- PyPI: `python-openstackclient` — affected >=0 <6.3.0

## Details
A flaw was found in OpenStack. When a user tries to delete a non-existing access rule in it's scope, it deletes other existing access rules which are not associated with any application credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6110
- https://github.com/openstack/python-openstackclient/commit/bc60e3bb908a7f10c87993d791184bfe46784d6c
- https://access.redhat.com/errata/RHSA-2024:2737
- https://access.redhat.com/errata/RHSA-2024:2769
- https://access.redhat.com/security/cve/CVE-2023-6110
- https://bugzilla.redhat.com/show_bug.cgi?id=2212960
- https://code.engineering.redhat.com/gerrit/gitweb?p=python-openstackclient.git;a=commit;h=7a7c364bdd7b2cd2b56e73724110710a68d58abf
- https://github.com/openstack/python-openstackclient
- https://review.opendev.org/c/openstack/python-openstackclient/+/888697
