# [C] OpenStack Mistral allows Arbitrary Remote Code Execution when the API is exposed

## Summary
Severity: Critical
Advisory: GHSA-9hfw-w3f4-c4p8
CVE: CVE-2026-41283
CWE: CWE-749, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-9hfw-w3f4-c4p8
Type: github-advisory

## Affected
- PyPI: `mistral` — affected >=20.0.0 <20.1.1
- PyPI: `mistral` — affected 21.0.0
- PyPI: `mistral` — affected 22.0.0

## Details
OpenStack Mistral through 22.0.0 allows Arbitrary Remote Code Execution when the API is exposed. There are endpoints that allow code execution, which can lead to exfiltration of service credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41283
- https://access.redhat.com/security/cve/CVE-2026-41283
- https://bugzilla.redhat.com/show_bug.cgi?id=2484607
- https://github.com/openstack/mistral
- https://github.com/openstack/mistral/tags
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-41283.json
- https://security.openstack.org/ossa/OSSA-2026-020.html
- https://www.openwall.com/lists/oss-security/2026/06/03/14
- http://www.openwall.com/lists/oss-security/2026/06/03/14
