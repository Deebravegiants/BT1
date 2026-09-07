# [M] openstack-heat may disclose sensitive information

## Summary
Severity: Medium
Advisory: GHSA-2fqr-cx7q-3ph8
CVE: CVE-2024-7319
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-02
Source: https://github.com/advisories/GHSA-2fqr-cx7q-3ph8
Type: github-advisory

## Affected
- PyPI: `openstack-heat` — affected >=0

## Details
An incomplete fix for CVE-2023-1625 was found in openstack-heat. Sensitive information may possibly be disclosed through the OpenStack stack abandon command with the hidden feature set to True and the CVE-2023-1625 fix applied.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7319
- https://access.redhat.com/security/cve/CVE-2024-7319
- https://bugzilla.redhat.com/show_bug.cgi?id=2258810
- https://github.com/openstack/heat
- https://storyboard.openstack.org/#!/story/2011007
