# [M] vrana/adminer via XSS in the history parameter in SQL command

## Summary
Severity: Medium
Advisory: GHSA-9pgx-gcph-mpqr
CVE: CVE-2020-35572
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-02-11
Source: https://github.com/advisories/GHSA-9pgx-gcph-mpqr
Type: github-advisory

## Affected
- Packagist: `vrana/adminer` — affected >=0 <4.7.9

## Details
### Impact
Users of Adminer versions supporting SQL command (most versions, e.g. MySQL) using browsers not encoding URL parameters before sending to server (likely Edge, not Chrome, not Firefox) are affected.

### Patches
Patched by 5c395afc, included in version [4.7.9](https://github.com/vrana/adminer/releases/tag/v4.7.9).

### Workarounds
Use browser which encodes URL parameters (e.g. Chrome or Firefox).

### References
https://sourceforge.net/p/adminer/bugs-and-features/775/

### For more information
If you have any questions or comments about this advisory:
* Comment at https://sourceforge.net/p/adminer/bugs-and-features/775/

## References
- https://github.com/vrana/adminer/security/advisories/GHSA-9pgx-gcph-mpqr
- https://nvd.nist.gov/vuln/detail/CVE-2020-35572
- https://github.com/vrana/adminer/commit/5c395afc098e501be3417017c6421968aac477bd
- https://github.com/vrana/adminer
- https://sourceforge.net/p/adminer/bugs-and-features/775
- https://sourceforge.net/p/adminer/news/2021/02/adminer-479-released
