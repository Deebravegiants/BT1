# [H] Denial of service vulnerability on Password reset page

## Summary
Severity: High
Advisory: GHSA-7j9h-3jxf-3vrf
CVE: CVE-2023-25171
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-02-15
Source: https://github.com/advisories/GHSA-7j9h-3jxf-3vrf
Type: github-advisory

## Affected
- PyPI: `kiwitcms` — affected >=0 <12.0

## Details
### Impact
Previous versions of Kiwi TCMS do not impose rate limits which makes it easier to attempt denial-of-service attacks against the Password reset page. An attacker could potentially send a large number of emails if they know the email addresses of users in Kiwi TCMS. Additionally that may strain SMTP resources. 

### Patches
Users should upgrade to v12.0 or later.

### Workarounds
Users may install and configure a rate-limiting proxy in front of Kiwi TCMS such as Nginx and/or configure rate limits on their email server when possible.

### References
[Disclosed by Ahmed Rabeaa Mosaa](https://huntr.dev/bounties/3b712cb6-3fa3-4f71-8562-7a7016c6262e)

## References
- https://github.com/kiwitcms/Kiwi/security/advisories/GHSA-7j9h-3jxf-3vrf
- https://nvd.nist.gov/vuln/detail/CVE-2023-25171
- https://github.com/kiwitcms/Kiwi/commit/761305d04f5910ba14cc04d1255a8f1afdbb87f3
- https://github.com/kiwitcms/Kiwi
- https://huntr.dev/bounties/3b712cb6-3fa3-4f71-8562-7a7016c6262e
- https://kiwitcms.org/blog/kiwi-tcms-team/2023/02/15/kiwi-tcms-120
