# [H] Cotonti: Stored Cross-Site Scripting in the Personal File Storage (PFS) module

## Summary
Severity: High
Advisory: GHSA-86hp-hf3j-3m8r
CVE: CVE-2026-55746
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-86hp-hf3j-3m8r
Type: github-advisory

## Affected
- Packagist: `cotonti/cotonti` — affected >=0

## Details
Cotonti 1.0.0 (master branch, commit f43f1fc3) is vulnerable to stored Cross-Site Scripting in the Personal File Storage (PFS) module. A folder title (pff_title) is imported with the 'TXT' filter, which does not strip or encode HTML (the tag check in cot_import is disabled), so an authenticated user can store HTML/JavaScript in a folder title. In modules/pfs/inc/pfs.main.php the title is assigned to the template variable PFF_ROW_TITLE without htmlspecialchars(), and modules/pfs/tpl/pfs.tpl outputs {PFF_ROW_TITLE} unescaped. When the folder listing is viewed (including by other users for public folders), the injected script executes in the victim's browser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-55746
- https://github.com/Cotonti/Cotonti
- https://github.com/Cotonti/Cotonti/blob/f43f1fc38ba4e02027786dad9dac1435c7c52b30/modules/pfs/inc/pfs.main.php#L396
