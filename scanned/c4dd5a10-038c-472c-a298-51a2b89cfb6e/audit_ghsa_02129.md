# [H] Mautic Sessions could be hijacked due to tracking contacts by an auto-incremented ID

## Summary
Severity: High
Advisory: GHSA-vfxj-qg93-7wwc
CVE: CVE-2018-10189
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-01-19
Source: https://github.com/advisories/GHSA-vfxj-qg93-7wwc
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <2.13.0

## Details
### Impact
An issue was discovered in Mautic 1.x and 2.x before 2.13.0. It is possible to systematically emulate tracking cookies per contact due to tracking the contact by their auto-incremented ID. Thus, a third party can manipulate the cookie value with +1 to systematically assume being tracked as each contact in Mautic. It is then possible to retrieve information about the contact through forms that have progressive profiling enabled.

### Patches
Update to 2.13.0 or later

### Workarounds
None

### For more information
If you have any questions or comments about this advisory:
* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-vfxj-qg93-7wwc
- https://nvd.nist.gov/vuln/detail/CVE-2018-10189
- https://github.com/mautic/mautic/releases/tag/2.13.0
