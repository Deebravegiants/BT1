# [M] dcnnt-py is vulnerable to command injection via Notification Handler

## Summary
Severity: Medium
Advisory: GHSA-8p42-7597-p2f6
CVE: CVE-2023-1000
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-04-27
Source: https://github.com/advisories/GHSA-8p42-7597-p2f6
Type: github-advisory

## Affected
- PyPI: `dcnnt` — affected >=0 <0.9.1

## Details
A vulnerability was found in cyanomiko dcnnt-py up to 0.9.0. It has been classified as critical. Affected is the function main of the file dcnnt/plugins/notifications.py of the component Notification Handler. The manipulation leads to command injection. It is possible to launch the attack remotely. Upgrading to version 0.9.1 is able to address this issue. The patch is identified as b4021d784a97e25151a5353aa763a741e9a148f5. It is recommended to upgrade the affected component. VDB-262230 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-1000
- https://github.com/cyanomiko/dcnnt-py/pull/23
- https://github.com/cyanomiko/dcnnt-py/commit/b4021d784a97e25151a5353aa763a741e9a148f5
- https://github.com/cyanomiko/dcnnt-py
- https://github.com/cyanomiko/dcnnt-py/releases/tag/0.9.1
- https://vuldb.com/?ctiid.262230
- https://vuldb.com/?id.262230
