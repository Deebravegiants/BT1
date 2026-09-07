# [M] Reportico Web fails to invalidate cookies upon logout

## Summary
Severity: Medium
Advisory: GHSA-2q2f-h83x-cx3x
CVE: CVE-2024-31556
CWE: CWE-269, CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-2q2f-h83x-cx3x
Type: github-advisory

## Affected
- Packagist: `reportico-web/reportico` — affected >=0

## Details
An issue in Reportico Web before v.8.1.0. This vulnerability arises from the failure of the web application to properly invalidate session cookies upon logout. When a user logs out of the application, the session cookie should be invalidated to prevent unauthorized access. However, due to the oversight in the application's implementation, the session cookie remains active even after logout. Consequently, if an attacker obtains the session cookie, they can exploit it to access the user's session and perform unauthorized actions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31556
- https://github.com/reportico-web/reportico/issues/53
- https://github.com/reportico-web/reportico
