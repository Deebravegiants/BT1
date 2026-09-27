# [M] Denial of service in neutron

## Summary
Severity: Medium
Advisory: GHSA-r3jh-qhgj-gvr8
CVE: CVE-2023-3637
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-r3jh-qhgj-gvr8
Type: github-advisory

## Affected
- PyPI: `neutron` — affected >=0

## Details
An uncontrolled resource consumption flaw was found in openstack-neutron. This flaw allows a remote authenticated user to query a list of security groups for an invalid project. This issue creates resources that are unconstrained by the user's quota. If a malicious user were to submit a significant number of requests, this could lead to a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3637
- https://access.redhat.com/errata/RHSA-2023:4283
- https://access.redhat.com/security/cve/CVE-2023-3637
- https://bugzilla.redhat.com/show_bug.cgi?id=2222270
