# [C] Cockpit CMS contains an arbitrary file upload vulenrability

## Summary
Severity: Critical
Advisory: GHSA-vpj8-xfqc-jcv9
CVE: CVE-2024-4825
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-vpj8-xfqc-jcv9
Type: github-advisory

## Affected
- Packagist: `cockpit-hq/cockpit` — affected >=0 <2.7.0

## Details
A vulnerability has been discovered in Agentejo Cockpit CMS v0.5.5 that consists in an arbitrary file upload in ‘/media/api’ parameter via post request. An attacker could upload files to the server, compromising the entire infrastructure.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-4825
- https://github.com/Cockpit-HQ/Cockpit
- https://www.incibe.es/en/incibe-cert/notices/aviso/unrestricted-upload-file-dangerous-type-vulnerability-cockpit-cms
