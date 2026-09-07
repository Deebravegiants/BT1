# [M] wlc: print_html outputs API data without HTML escaping

## Summary
Severity: Medium
Advisory: GHSA-gx2m-mcc2-r4p3
CVE: CVE-2026-42150
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-gx2m-mcc2-r4p3
Type: github-advisory

## Affected
- PyPI: `wlc` — affected >=0 <2.0.0

## Details
### Impact
The HTML output format in wlc embeds API response data into HTML without escaping, allowing cross-site scripting when the output is rendered in a browser.


### Patches
* https://github.com/WeblateOrg/wlc/pull/1327

### Workarounds
The only vulnerable code path is HTML output which is opt-in.

### References
Weblate thanks @fg0x0 for reporting this on GitHub.

## References
- https://github.com/WeblateOrg/wlc/security/advisories/GHSA-gx2m-mcc2-r4p3
- https://nvd.nist.gov/vuln/detail/CVE-2026-42150
- https://github.com/WeblateOrg/wlc/pull/1327
- https://github.com/WeblateOrg/wlc/commit/0f3e58f6d7457b05d48ef40f579a172c4c8b8469
- https://github.com/WeblateOrg/wlc
- https://github.com/WeblateOrg/wlc/releases/tag/2.0.0
