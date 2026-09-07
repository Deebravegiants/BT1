# [H] mppx: Tempo has a session close voucher bypass vulnerability due to settled amount equality

## Summary
Severity: High
Advisory: GHSA-mv9j-8jvg-j8mr
CVE: CVE-2026-34209
CWE: CWE-294
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-mv9j-8jvg-j8mr
Type: github-advisory

## Affected
- npm: `mppx` — affected >=0 <0.4.11

## Details
### Impact

The `tempo/session` cooperative close handler validated the close voucher amount using `<` instead of `<=` against the on-chain settled amount. An attacker could submit a close voucher exactly equal to the settled amount, which would be accepted without committing any new funds, effectively closing or griefing the channel for free.

### Patches

Fixed in 0.4.11.

### Workarounds

There are no workarounds available for this vulnerability.

## References
- https://github.com/wevm/mppx/security/advisories/GHSA-mv9j-8jvg-j8mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-34209
- https://github.com/wevm/mppx/commit/94088246ee18f21b5d6be40d9e7a464f5a280bfb
- https://github.com/wevm/mppx
- https://github.com/wevm/mppx/releases/tag/mppx@0.4.11
