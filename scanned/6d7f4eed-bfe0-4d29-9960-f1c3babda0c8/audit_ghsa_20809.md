# [M] openstack-barbican Denial of Service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6p2h-rjj7-2j63
CVE: CVE-2022-23452
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-02
Source: https://github.com/advisories/GHSA-6p2h-rjj7-2j63
Type: github-advisory

## Affected
- PyPI: `barbican` — affected >=0 <14.0.0

## Details
An authorization flaw was found in openstack-barbican, where anyone with an admin role could add secrets to a different project container. This flaw allows an attacker on the network to consume protected resources and cause a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23452
- https://github.com/openstack/barbican/commit/6c841b23afa8ed6fa4cd01ba1a6bebfb60f06ae5
- https://access.redhat.com/errata/RHSA-2022:5114
- https://access.redhat.com/errata/RHSA-2022:8874
- https://access.redhat.com/security/cve/CVE-2022-23452
- https://bugzilla.redhat.com/show_bug.cgi?id=2022908
- https://bugzilla.redhat.com/show_bug.cgi?id=2025090
- https://review.opendev.org/c/openstack/barbican/+/814200
- https://storyboard.openstack.org/#!/story/2009297
- https://storyboard.openstack.org/#%21/story/2009297
