# [H] Directus Allows Single Sign-On User Enumeration

## Summary
Severity: High
Advisory: GHSA-jgf4-vwc3-r46v
CVE: CVE-2024-39896
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-jgf4-vwc3-r46v
Type: github-advisory

## Affected
- npm: `directus` — affected >=9.11 <10.13.0

## Details
### Impact
When relying on SSO providers in combination with local authentication it can be possible to enumerate existing SSO users in the instance. This is possible because if an email address exists in Directus and belongs to a known SSO provider then it will throw a "helpful" error that the user belongs to another provider.

### Reproduction

1. Create a user using a SSO provider `test@directus.io`.
2. Try to log-in using the regular login form (or the API)
3. When using a valid email address

| **APP** | **API** |
| --- | --- |
| ![image](https://github.com/directus/directus/assets/9389634/1da3301d-226f-46a7-bfb8-3f6fb9bc55cd) | ![image](https://github.com/directus/directus/assets/9389634/50cab310-7d1c-4241-a6be-d06542565767) |

4. When using an invalid email address

| **APP** | **API** |
| --- | --- |
| ![image](https://github.com/directus/directus/assets/9389634/7b97659e-b49c-410b-872e-e36786b6e41e) | ![image](https://github.com/directus/directus/assets/9389634/d26ccba7-bb27-437e-991e-99c10941bbe7) |

5. Using this differing error it is possible to determine whether a specific email address is present in the Directus instance as an SSO user.

### Workarounds
When only using SSO for authentication then you can work around this issue by disabling local login using the following environment variable `AUTH_DISABLE_DEFAULT="true"`

### References
Implemented as feature in https://github.com/directus/directus/pull/13184
https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account

## References
- https://github.com/directus/directus/security/advisories/GHSA-jgf4-vwc3-r46v
- https://nvd.nist.gov/vuln/detail/CVE-2024-39896
- https://github.com/directus/directus/commit/454cb534d6ffa547feb11f4d74b932ae7368dae2
- https://github.com/directus/directus
