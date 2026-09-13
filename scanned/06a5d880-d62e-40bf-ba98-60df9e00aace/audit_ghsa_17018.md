# [H] NiceGUI allows potential access to local file system

## Summary
Severity: High
Advisory: GHSA-mwc7-64wg-pgvj
CVE: CVE-2024-32005
CWE: CWE-22, CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2024-04-12
Source: https://github.com/advisories/GHSA-mwc7-64wg-pgvj
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=1.4.6 <1.4.21

## Details
NiceGUI is an easy-to-use, Python-based UI framework. A local file inclusion is present in the NiceUI leaflet component when requesting resource files under the `/_nicegui/{__version__}/resources/{key}/{path:path}` route. 

As a result any file on the backend filesystem which the web server has access to can be read by an attacker with access to the NiceUI leaflet website. 

This vulnerability has been addressed in version 1.4.21. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-mwc7-64wg-pgvj
- https://nvd.nist.gov/vuln/detail/CVE-2024-32005
- https://github.com/zauberzeug/nicegui/commit/ed12eb14f2a6c48b388a05c04b3c5a107ea9d330
- https://github.com/zauberzeug/nicegui
- https://huntr.com/bounties/29ec621a-bd69-4225-ab0f-5bb8a1d10c67
