# [M] MantisBT Vulnerable to Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: GHSA-99jc-wqmr-ff2q
CVE: CVE-2024-34080
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-05-13
Source: https://github.com/advisories/GHSA-99jc-wqmr-ff2q
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.26.2

## Details
If an issue references a note that belongs to another issue that the user doesn't have access to, then it gets hyperlinked. Clicking on the link gives an access denied error as expected, yet some information remains available via the link, link label, and tooltip.

### Impact
Disclosure of the following information:
- existence of the note
- note author name
- note creation timestamp
- issue id the note belongs to

### Patches
See PR https://github.com/mantisbt/mantisbt/pull/2000

### Workarounds
None

### References
https://mantisbt.org/bugs/view.php?id=34434

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-99jc-wqmr-ff2q
- https://nvd.nist.gov/vuln/detail/CVE-2024-34080
- https://github.com/mantisbt/mantisbt/pull/2000
- https://github.com/mantisbt/mantisbt/commit/0a50562369d823689c9b946066d1e49d3c2df226
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=34434
