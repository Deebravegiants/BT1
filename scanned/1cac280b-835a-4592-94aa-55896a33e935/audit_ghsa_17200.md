# [H] GoogleOAuthenticator.hosted_domain incorrectly verifies membership of an Google organization/workspace

## Summary
Severity: High
Advisory: GHSA-55m3-44xf-hg4h
CVE: CVE-2024-29033
CWE: CWE-285
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-03-20
Source: https://github.com/advisories/GHSA-55m3-44xf-hg4h
Type: github-advisory

## Affected
- PyPI: `oauthenticator` — affected >=0 <16.3.0

## Details
## Summary and impact

[`GoogleOAuthenticator.hosted_domain`] is used to restrict what Google accounts can be authorized to access a JupyterHub. The restriction _is intended_ to ensure Google accounts are part of one or more Google organizations/workspaces verified to control specified domain(s).

The vulnerability is that the actual restriction has been to Google accounts with emails ending with the domain. Such accounts could have been created by anyone which at one time was able to read an email associated with the domain. This was described by Dylan Ayrey (@dxa4481) in this [blog post] from 15th December 2023.

## Remediation

Upgrade to `oauthenticator>=16.3.0` or restrict who can login another way, such as [`allowed_users`] or [`allowed_google_groups`].

[`GoogleOAuthenticator.hosted_domain`]: https://oauthenticator.readthedocs.io/en/latest/reference/api/gen/oauthenticator.google.html#oauthenticator.google.GoogleOAuthenticator.hosted_domain
[`allowed_users`]: https://oauthenticator.readthedocs.io/en/latest/reference/api/gen/oauthenticator.google.html#oauthenticator.google.GoogleOAuthenticator.allowed_users
[`allowed_google_groups`]: https://oauthenticator.readthedocs.io/en/latest/reference/api/gen/oauthenticator.google.html#oauthenticator.google.GoogleOAuthenticator.allowed_google_groups
[blog post]: https://trufflesecurity.com/blog/google-oauth-is-broken-sort-of/

## References
- https://github.com/jupyterhub/oauthenticator/security/advisories/GHSA-55m3-44xf-hg4h
- https://nvd.nist.gov/vuln/detail/CVE-2024-29033
- https://github.com/jupyterhub/oauthenticator/commit/5246b09675501b09fb6ed64022099b7644812f60
- https://github.com/jupyterhub/oauthenticator
- https://trufflesecurity.com/blog/google-oauth-is-broken-sort-of
