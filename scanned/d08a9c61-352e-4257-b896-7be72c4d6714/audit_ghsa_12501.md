# [M] PHPEMS Deserialization of Untrusted Data vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5rv2-vvmf-f7w8
CVE: CVE-2023-6654
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-12-10
Source: https://github.com/advisories/GHSA-5rv2-vvmf-f7w8
Type: github-advisory

## Affected
- Packagist: `phpems/phpems` — affected >=6.0.0

## Details
A vulnerability classified as critical was found in PHPEMS 6.x/7.0. Affected by this vulnerability is an unknown functionality in the library lib/session.cls.php of the component Session Data Handler. The manipulation leads to deserialization. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. The identifier VDB-247357 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-6654
- https://github.com/oiuv/phpems
- https://github.com/oiuv/phpems/blob/a4a049362a0250c4b1762464b34d90ed881fef19/lib/session.cls.php
- https://note.zhaoj.in/share/jw4Hp9cq7T69
- https://vuldb.com/?ctiid.247357
- https://vuldb.com/?id.247357
