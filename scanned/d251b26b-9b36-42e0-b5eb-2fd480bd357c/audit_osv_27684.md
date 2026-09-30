# [H] Open Forms potential multi-factor authentication bypass

## Summary
Severity: High
Advisory: CVE-2024-24771
Aliases: GHSA-64r3-x3gf-vp63
CVSS: 7.7 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2024-02-07
Source: https://osv.dev/vulnerability/CVE-2024-24771
Type: osv

## Details
Open Forms allows users create and publish smart forms. Versions prior to 2.2.9, 2.3.7, 2.4.5, and 2.5.2 contain a non-exploitable multi-factor authentication weakness. Superusers who have their credentials (username + password) compromised could potentially have the second-factor authentication bypassed if an attacker somehow managed to authenticate to Open Forms. The maintainers of Open Forms do not believe it is or has been possible to perform this login. However, if this were possible, the victim's account may be abused to view (potentially sensitive) submission data or have been used to impersonate other staff accounts to view and/or modify data. Three mitigating factors to help prevent exploitation include: the usual login page (at `/admin/login/`) does not fully log in the user until the second factor was succesfully provided; the additional non-MFA protected login page at `/api/v2/api-authlogin/` was misconfigured and could not be used to log in; and there are no additional ways to log in. This also requires credentials of a superuser to be compromised to be exploitable. Versions 2.2.9, 2.3.7, 2.4.5, and 2.5.2 contain the following patches to address these weaknesses: Move and only enable the API auth endpoints (`/api/v2/api-auth/login/`) with `settings.DEBUG = True`. `settings.DEBUG = True` is insecure and should never be applied in production settings. Additionally, apply a custom permission check to the hijack flow to only allow second-factor-verified superusers to perform user hijacking.

## References
- https://github.com/open-formulieren/open-forms/releases/tag/2.2.9
- https://github.com/open-formulieren/open-forms/releases/tag/2.3.7
- https://github.com/open-formulieren/open-forms/releases/tag/2.4.5
- https://github.com/open-formulieren/open-forms/releases/tag/2.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/24xxx/CVE-2024-24771.json
- https://github.com/open-formulieren/open-forms/security/advisories/GHSA-64r3-x3gf-vp63
- https://nvd.nist.gov/vuln/detail/CVE-2024-24771
