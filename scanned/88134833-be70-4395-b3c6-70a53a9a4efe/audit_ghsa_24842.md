# [M] Subrion CMS XSS

## Summary
Severity: Medium
Advisory: GHSA-c8mg-wp7h-f2pf
CVE: CVE-2018-14835
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-c8mg-wp7h-f2pf
Type: github-advisory

## Affected
- Packagist: `intelliants/subrion` — affected >=0

## Details
Subrion CMS v4.2.1 is vulnerable to Stored XSS because of no escaping added to the tooltip information being displayed in multiple areas.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14835
- https://github.com/intelliants/subrion/issues/760
- https://github.com/intelliants/subrion/pull/763
- https://github.com/intelliants/subrion/commit/a33a224c6c9e25144d828f92f6141c719215094b
- https://github.com/intelliants/subrion
