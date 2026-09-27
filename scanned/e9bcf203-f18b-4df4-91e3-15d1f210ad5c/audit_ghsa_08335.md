# [M] OpenStack Ironic: Pre-Validation Checksum Calculation allows Denial of Service (DoS) via Infinite Block Devices

## Summary
Severity: Medium
Advisory: GHSA-4g73-w726-53h3
CVE: CVE-2026-44919
CWE: CWE-696
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-4g73-w726-53h3
Type: github-advisory

## Affected
- PyPI: `ironic` — affected >=0

## Details
In OpenStack Ironic through 35.x before a3f6d73, during image handling, an infinite loop in checksum calculations can occur via the file:///dev/zero URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44919
- https://bugs.launchpad.net/ironic/+bug/2150332
- https://opendev.org/openstack/ironic
- https://opendev.org/openstack/ironic/commit/a3f6d735ac3642ab95b49142c7305f072ae748d0
- https://security.openstack.org/ossa/OSSA-2026-013.html
