# [H] No protection against brute-force attacks on login page

## Summary
Severity: High
Advisory: GHSA-7968-h4m4-ghm9
CVE: CVE-2023-25156
CWE: CWE-307
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-7968-h4m4-ghm9
Type: github-advisory

## Affected
- PyPI: `kiwitcms` — affected >=0 <12.0

## Details
### Impact
Previous versions of Kiwi TCMS do not impose rate limits which makes it easier to attempt brute-force attacks against the login page.

### Patches
Users should upgrade to v12.0 or later.

### Workarounds
Users may install and configure a rate-limiting proxy in front of Kiwi TCMS. For example nginx.

### References
[Disclosed by spyata](https://huntr.dev/bounties/2b1a9be9-45e9-490b-8de0-26a492e79795/)

## References
- https://github.com/kiwitcms/Kiwi/security/advisories/GHSA-7968-h4m4-ghm9
- https://nvd.nist.gov/vuln/detail/CVE-2023-25156
- https://github.com/kiwitcms/Kiwi/commit/0ed213fa0ddb7a6dc77e3c3b99e8fc90ccdaf46f
- https://github.com/kiwitcms/Kiwi
- https://huntr.dev/bounties/2b1a9be9-45e9-490b-8de0-26a492e79795
- https://kiwitcms.org/blog/kiwi-tcms-team/2023/02/15/kiwi-tcms-120
