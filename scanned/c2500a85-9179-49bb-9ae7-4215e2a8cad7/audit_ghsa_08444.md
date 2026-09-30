# [H] OpenStack Ironic has an Incorrect Resource Transfer Between Spheres

## Summary
Severity: High
Advisory: GHSA-54w4-233h-x86g
CVE: CVE-2026-42997
CWE: CWE-669
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-54w4-233h-x86g
Type: github-advisory

## Affected
- PyPI: `ironic-python-agent` — affected >=33.0.0 <35.0.1
- PyPI: `ironic-python-agent` — affected >=30.0.0 <32.0.1
- PyPI: `ironic-python-agent` — affected >=27.0.0 <29.0.5
- PyPI: `ironic-python-agent` — affected >=0 <26.1.6

## Details
An issue was discovered in idrac in OpenStack Ironic before 35.0.1. During import, a user invoking molds can request authorization to be sent to a remote endpoint. The credential forwarded is a time-limited Keystone token (which provides access to all OpenStack services Ironic is authorized for); or basic credentials configured for molds storage. The fixed versions are 26.1.6, 29.0.5, 32.0.1, and 35.0.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-42997
- https://github.com/openstack/ironic-python-agent
- https://security.openstack.org/ossa/OSSA-2026-010.html
- https://www.openwall.com/lists/oss-security/2026/05/05/10
- http://www.openwall.com/lists/oss-security/2026/05/05/10
