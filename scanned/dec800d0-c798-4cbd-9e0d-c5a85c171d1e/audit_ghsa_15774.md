# [H] Automad arbitrary file upload vulnerability

## Summary
Severity: High
Advisory: GHSA-47mc-qmh2-mqj4
CVE: CVE-2024-40400
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-19
Source: https://github.com/advisories/GHSA-47mc-qmh2-mqj4
Type: github-advisory

## Affected
- Packagist: `automad/automad` — affected >=0 <2.0.0-alpha.5

## Details
An arbitrary file upload vulnerability in the image upload function of Automad v2.0.0 allows attackers to execute arbitrary code via a crafted file.

The malicious file has to be prepared and uploaded manually by the admin. Usually there is only one admin per site and that is the owner.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-40400
- https://github.com/marcantondahmen/automad/issues/106
- https://github.com/marcantondahmen/automad/commit/112f070ccf423931c9bb2b36f9a26c345e1ef56e
- https://github.com/marcantondahmen/automad
