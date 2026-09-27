# [M] OpenStack Ironic allows file overwrite via directory traversal during deployment with a crafted ISO image

## Summary
Severity: Medium
Advisory: GHSA-9v62-qx4c-44x5
CVE: CVE-2026-48681
CWE: CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-9v62-qx4c-44x5
Type: github-advisory

## Affected
- PyPI: `ironic` — affected >=17.0.0 <26.1.7
- PyPI: `ironic` — affected >=27.0.0 <29.0.6
- PyPI: `ironic` — affected >=30.0.0 <32.0.2
- PyPI: `ironic` — affected >=33.0.0 <35.0.2

## Details
OpenStack Ironic through before 35.0.2 allows file overwrite via directory traversal during deployment with a crafted ISO image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-48681
- https://bugs.launchpad.net/ironic/+bug/2148333
- https://github.com/openstack/ironic
- https://www.openwall.com/lists/oss-security/2026/06/03/12
- http://www.openwall.com/lists/oss-security/2026/06/03/12
