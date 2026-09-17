# [M] parisneo/lollms has an insufficient session expiration vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8jg2-726g-xh43
CVE: CVE-2026-1163
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-8jg2-726g-xh43
Type: github-advisory

## Affected
- PyPI: `lollms` — affected >=0

## Details
An insufficient session expiration vulnerability exists in the latest version of parisneo/lollms. The application fails to invalidate active sessions after a password reset, allowing an attacker to continue using an old session token. This issue arises due to the absence of logic to reject requests after a period of inactivity and the excessively long default session duration of 31 days. The vulnerability enables an attacker to maintain persistent access to a compromised account, even after the victim resets their password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1163
- https://github.com/ParisNeo/lollms
- https://huntr.com/bounties/abe2d1c4-c21c-4608-8a8e-274565246a8b
