# [M] Froxlor allows Multiple Accounts to Share the Same Email Address Leading to Potential Privilege Escalation or Account Takeover

## Summary
Severity: Medium
Advisory: GHSA-7j6w-p859-464f
CVE: CVE-2025-29773
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-03-11
Source: https://github.com/advisories/GHSA-7j6w-p859-464f
Type: github-advisory

## Affected
- Packagist: `froxlor/froxlor` — affected >=0 <2.2.6

## Details
### Summary
the vulnerability is that users (such as resellers or customers) are able to create accounts with the same email address as an existing account (e.g., if the admin has [admin@froxlor.com](mailto:admin@froxlor.com), others can also create an account using the same email). This creates potential issues with account identification and security.

### Impact
Local/Authenticated: This vulnerability can be exploited by authenticated users (e.g., reseller, customer) who can create accounts with the same email address that has already been used by another account, such as the admin.
Email-based: The attack vector is email-based, as the system does not prevent multiple accounts from registering the same email address, leading to possible conflicts and security issues.

## References
- https://github.com/froxlor/Froxlor/security/advisories/GHSA-7j6w-p859-464f
- https://nvd.nist.gov/vuln/detail/CVE-2025-29773
- https://github.com/froxlor/Froxlor/commit/a43d53d54034805e3e404702a01312fa0c40b623
- https://github.com/froxlor/Froxlor
- https://mega.nz/file/h8oFHQrL#I4V02_BWee4CCx7OoBl_2Ufkd5Wc7fvs5aCatGApkoQ
