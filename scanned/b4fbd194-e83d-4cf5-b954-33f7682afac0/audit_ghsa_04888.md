# [H] Cotonti: Cross-Site Request Forgery in the Personal File Storage (PFS) module

## Summary
Severity: High
Advisory: GHSA-wx35-cv59-9gwr
CVE: CVE-2026-55744
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-wx35-cv59-9gwr
Type: github-advisory

## Affected
- Packagist: `cotonti/cotonti` — affected >=0

## Details
Cotonti 1.0.0 (master branch, commit f43f1fc3) is vulnerable to Cross-Site Request Forgery in the Personal File Storage (PFS) module. In modules/pfs/inc/pfs.main.php, the file upload action ('a=upload') processes uploaded files without calling cot_check_xg() to validate the anti-CSRF token, even though sibling actions such as 'delete' (line 272) do. A remote attacker who lures an authenticated user into visiting a malicious page can force the browser to submit a forged multipart request that uploads arbitrary files into the victim's PFS storage.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-55744
- https://github.com/Cotonti/Cotonti
- https://github.com/Cotonti/Cotonti/blob/f43f1fc38ba4e02027786dad9dac1435c7c52b30/modules/pfs/inc/pfs.main.php#L118
