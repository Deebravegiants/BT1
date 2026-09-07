# [H] Injection in UserFrosting

## Summary
Severity: High
Advisory: GHSA-cv25-3gmg-c6m8
CVE: CVE-2021-25994
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-cv25-3gmg-c6m8
Type: github-advisory

## Affected
- Packagist: `userfrosting/userfrosting` — affected >=0.3.1 <4.6.3

## Details
In Userfrosting, versions v0.3.1 to v4.6.2 are vulnerable to Host Header Injection. By luring a victim application user to click on a link, an unauthenticated attacker can use the “forgot password” functionality to reset the victim’s password and successfully take over their account.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25994
- https://github.com/userfrosting/UserFrosting/commit/796dd78757902435d1bd286415feea78098e45ba
- https://github.com/userfrosting/UserFrosting
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25994
