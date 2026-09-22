# [M] Authorization Bypass Through User-Controlled Key when using CILogonOAuthenticator oauthenticator

## Summary
Severity: Medium
Advisory: GHSA-r7v4-jwx9-wx43
CVE: CVE-2022-31027
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-06
Source: https://github.com/advisories/GHSA-r7v4-jwx9-wx43
Type: github-advisory

## Affected
- PyPI: `oauthenticator` — affected >=0 <15.0.0

## Details
# Background

CILogon is a federated auth provider that allows users to authenticate
themselves via a number of Identity Providers (IdP), focused primarily on educational and
research institutions (such as Universities). More traditional and open IdPs
such as GitHub, ORCID, Google, Microsoft, etc are also supported.

CILogonOAuthenticator is provided by the OAuthenticator package, and lets users log
in to a JupyterHub via CILogon. This is primarily used to restrict a JupyterHub
only to users of a given institute. The allowed_idps configuration trait of
CILogonOAuthenticator is documented to be a list of domains that indicate the
institutions whose users are authorized to access this JupyterHub. This authorization
is validated by ensuring that the *email* field provided to us by CILogon has a
*domain* that matches one of the domains listed in `allowed_idps`.

# Impact

If `allowed_idps` contains `berkeley.edu`, you might expect only users with valid
current credentials provided by University of California, Berkeley to be able to
access the JupyterHub. However, CILogonOAuthenticator does *not* verify which provider
is used by the user to login, only the email address provided. So a user can login
with a GitHub account that has email set to `<something>@berkeley.edu`, and that will
be treated exactly the same as someone logging in using the UC Berkeley official
Identity Provider. This has two consequences:

1. Since GitHub (and most other providers we tested) only require you to verify
   your email once, a user can access a JupyterHub even if their access to
   the institution's IdP has been revoked or expired.
2. CILogon supports hundreds of identity providers - if even one of them allows
   users to set any email ids without verifying, that can be used to impersonate
   *any* user on any other identity provider! While CILogon itself has a stellar
   security record, this particular method of doing authorization means an attacker
   would only need to compromise a single identity provider to compromise all of
   CILogon

We currently do not know of any identity provider that provides *unverified*
email addresses to CILogon, so this is not a severe known vulnerability. However,
there are hundreds of IdPs, and we could not try them all.

# Patches

This patch makes a *breaking change* in how `allowed_idps` is interpreted. It's
no longer a list of domains, but configuration representing the `EntityID` of the
IdPs that are allowed, picked from the [list maintained by CILogon](https://cilogon.org/idplist/).
So instead of `berkeley.edu`, you would specify `urn:mace:incommon:berkeley.edu` to
allow logins from users currently with `berkeley.edu` accounts. GitHub users
with a verified `berkeley.edu` email will no longer be allowed to log in.

For details on how to transition your CILogonOAuthenticator configuration to the patched version 15.0.0 or above, see [the migration](https://oauthenticator.readthedocs.io/en/latest/migrations.html) documentation.

## References
- https://github.com/jupyterhub/oauthenticator/security/advisories/GHSA-r7v4-jwx9-wx43
- https://nvd.nist.gov/vuln/detail/CVE-2022-31027
- https://github.com/jupyterhub/oauthenticator/commit/5cd2d1816f90dc5c946e6e38fd2d0ba535624c5c
- https://github.com/jupyterhub/oauthenticator
- https://github.com/pypa/advisory-database/tree/main/vulns/oauthenticator/PYSEC-2022-206.yaml
