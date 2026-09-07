# [H] NocoDB: Stored Cross-Site Scripting via Row Comments

## Summary
Severity: High
Advisory: GHSA-jf3g-4gwg-4h66
CVE: CVE-2026-47383
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-jf3g-4gwg-4h66
Type: github-advisory

## Affected
- npm: `nocodb` — affected >=0 <2026.05.1

## Details
### Summary
An authenticated commenter could store HTML in row comments that executed as script
when other users hovered over the comment in the expanded form view.

### Details
The comment write paths persisted the raw comment body with no server-side sanitisation;
the expanded-form sidebar then rendered the stored body and fed its `data-tooltip`
attribute to Tippy with `allowHTML: true`. Even when the editor stripped script tags
at write time, attribute-level payloads re-entered the DOM as live HTML on hover.

### Impact
Stored Cross-Site Scripting against any user who views the affected row. Script runs in
the NocoDB origin with the victim's session and can read the auth JWT from
`localStorage`. Authentication and comment permission are required.

### Credit
This issue was reported by [@DavidCarliez](https://github.com/DavidCarliez). It was independently reported by [@Mouhebbenelwafi](https://github.com/Mouhebbenelwafi).

## References
- https://github.com/nocodb/nocodb/security/advisories/GHSA-jf3g-4gwg-4h66
- https://nvd.nist.gov/vuln/detail/CVE-2026-47383
- https://github.com/nocodb/nocodb
- https://github.com/nocodb/nocodb/releases/tag/2026.05.1
