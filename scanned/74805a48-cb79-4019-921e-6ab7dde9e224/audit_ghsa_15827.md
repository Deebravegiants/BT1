# [M] OpenStack Ironic fails to verify checksums of supplied image_source URLs

## Summary
Severity: Medium
Advisory: GHSA-8h22-6qwx-q4w9
CVE: CVE-2024-47211
CWE: CWE-354
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-10-04
Source: https://github.com/advisories/GHSA-8h22-6qwx-q4w9
Type: github-advisory

## Affected
- PyPI: `ironic` — affected >=25.0.0 <26.1.1
- PyPI: `ironic` — affected >=23.1.0 <24.1.3
- PyPI: `ironic` — affected >=22.0.0 <23.0.3
- PyPI: `ironic` — affected >=0

## Details
In OpenStack Ironic before 21.4.4, 22.x and 23.x before 23.0.3, 23.x and 24.x before 24.1.3, and 25.x and 26.x before 26.1.0, there is a lack of checksum validation of supplied image_source URLs when configured to convert images to a raw format for streaming.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47211
- https://github.com/openstack/ironic/commit/2127cc4c93770778457fde0582c1bba258c67e02
- https://github.com/openstack/ironic/commit/7a1292c569a84eb05806a57a89fca5bb6b0c4043
- https://github.com/openstack/ironic/commit/ebce0fd0845de411171127a55002ae7c9605de57
- https://github.com/openstack/ironic
- https://github.com/openstack/ironic/compare/24.1.2...26.1.0
- https://github.com/openstack/ironic/security
- https://github.com/openstack/ironic/tags
- https://security.openstack.org/ossa/OSSA-2024-004.html
