# [M] Hail relies on OIDC email claims to verify the validity of a user's domain.

## Summary
Severity: Medium
Advisory: GHSA-487p-qx68-5vjw
CVE: CVE-2023-51663
CWE: CWE-289
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-01-02
Source: https://github.com/advisories/GHSA-487p-qx68-5vjw
Type: github-advisory

## Affected
- PyPI: `hail` — affected >=0 <0.2.127

## Details
### Impact

All Hail Batch clusters are affected. An attacker is able to:

1. Create one or more accounts with Hail Batch without corresponding real accounts in the organization.

For example, a user could create a Microsoft or Google account and then change their email to "inconspicuous@example.org". This Microsoft or Google account can then be used to create a Hail Batch account in Hail Batch clusters whose organization domain is "example.org".

In Google, this attack is partially mitigated because Google requires users to verify ownership of their Google account. However, a valid user is able to create multiple distinct Hail Batch accounts by creating multiple distinct Google accounts using email addresses of the form "real_user_email_name+random_id@example.org".

In Microsoft, this attack requires Azure AD Administrator access to an Azure AD Tenant. The Azure AD Administrator is permitted to change the email address of an account to any other email address without verification. An attacker can create an Azure Tenant for free.

1. The attacker *does not* have access to any private data (because the new service principals or service accounts are not granted any privileges).
3. If trial Hail Batch billing projects are enabled, the attacker *does* have the ability to run jobs and thus spend money. An attacker can create as many accounts as Microsoft or Google permit.
4. The attacker *cannot* impersonate another user because, in Azure, we use the `sub` from the OAuth2 response, and, in Google, Google does an email verification.

### Remediation

1. Apply this patch to prevent third-party attackers from creating accounts.
2. Audit your users list https://auth.example.org/users for user accounts whose login ids are not valid login ids with your identity provider. Delete such users.

A forthcoming change will prevent users from creating multiple accounts using Google's `+` email redirection.

### Workarounds
None.

### References
1. https://trufflesecurity.com/blog/google-oauth-is-broken-sort-of/
2. https://www.descope.com/blog/post/noauth
4. https://developers.google.com/identity/openid-connect/openid-connect#an-id-tokens-payload
5. https://learn.microsoft.com/en-us/entra/identity-platform/access-token-claims-reference#payload-claims

[1] Hail Batch must separately stop using emails and start using the OAuth2 `sub` in Google. This is a known deficiency. In particular, if an email is re-used by the organization for a new user, the new user could access the old user's Hail Batch account.

## References
- https://github.com/hail-is/hail/security/advisories/GHSA-487p-qx68-5vjw
- https://nvd.nist.gov/vuln/detail/CVE-2023-51663
- https://github.com/hail-is/hail/commit/0dcc17ff24564b6f5592261d7975e8afd0f95de7
- https://github.com/hail-is/hail
- https://github.com/pypa/advisory-database/tree/main/vulns/hail/PYSEC-2023-271.yaml
