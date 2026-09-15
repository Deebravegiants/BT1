# [C] Akeneo PIM vulnerable to shell injection in the mass edition

## Summary
Severity: Critical
Advisory: GHSA-q8cr-xphm-7gfv
CVE: CVE-2017-1000009
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q8cr-xphm-7gfv
Type: github-advisory

## Affected
- Packagist: `akeneo/pim-community-dev` — affected >=1.4 <1.4.28
- Packagist: `akeneo/pim-community-dev` — affected >=1.5 <1.5.15
- Packagist: `akeneo/pim-community-dev` — affected >=1.6 <1.6.6

## Details
Akeneo PIM CE and EE <1.6.6, <1.5.15, <1.4.28 are vulnerable to shell injection in the mass edition, resulting in remote execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000009
- https://github.com/akeneo/pim-community-dev
- https://github.com/akeneo/pim-community-dev/blob/1.5/CHANGELOG-1.5.md#bug-fixes-2
- https://github.com/akeneo/pim-community-dev/blob/master/CHANGELOG-1.4.md#bug-fixes
- https://github.com/akeneo/pim-community-dev/blob/master/CHANGELOG-1.6.md#bug-fixes-2
