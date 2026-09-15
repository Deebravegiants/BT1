# [M] glance-store logs s3 access keys

## Summary
Severity: Medium
Advisory: GHSA-wgpq-p2hm-56v9
CVE: CVE-2024-1141
CWE: CWE-532, CWE-779
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-01
Source: https://github.com/advisories/GHSA-wgpq-p2hm-56v9
Type: github-advisory

## Affected
- PyPI: `glance-store` — affected >=0

## Details
A vulnerability was found in python-glance-store. The issue occurs when the package logs the access_key for the glance-store when the DEBUG log level is enabled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1141
- https://github.com/openstack/glance_store/commit/d6e531af4821c8466b1e9404f12f89f6216417f2
- https://access.redhat.com/errata/RHSA-2024:2732
- https://access.redhat.com/security/cve/CVE-2024-1141
- https://bugzilla.redhat.com/show_bug.cgi?id=2258836
- https://github.com/openstack/glance_store
