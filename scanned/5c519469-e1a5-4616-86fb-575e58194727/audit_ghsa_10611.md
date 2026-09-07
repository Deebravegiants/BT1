# [H] Auth0OAuthenticator has an Authentication Bypass via Unverified Email Claims

## Summary
Severity: High
Advisory: GHSA-rrvg-cxh4-qhrv
CVE: CVE-2026-33175
CWE: CWE-287, CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-rrvg-cxh4-qhrv
Type: github-advisory

## Affected
- PyPI: `oauthenticator` — affected >=0 <17.4.0

## Details
### Summary

An authentication bypass vulnerability in `oauthenticator` allows an attacker with an unverified email address on an Auth0 tenant to login to JupyterHub. When `email` is used as the usrname_claim, this gives users control over their username and the possibility of account takeover.

### Impact

This is an **Authentication Bypass Vulnerability**. Any Auth0 tenant leveraging the `Auth0OAuthenticator` mapping the `email` claim to the JupyterHub username is impacted. By default, Auth0 handles email verification as a user flag, not a hard block to authentication streams. If an attacker can register an account with the Auth0 tenant with an unverified email and knows the email of an existing user on the system, they can authenticate as that user.

### Patches

- Upgrade oauthenticator to 17.4

### Workarounds

- Check `email_verified` field in an `Authenticator.post_auth_hook` function
- Do not use `email` as the username claim
- [Enforce email verification in auth0](https://support.auth0.com/center/s/article/Enforce-Email-Verification-With-Sending-Email-After-Each-Denied-Access)

## References
- https://github.com/jupyterhub/oauthenticator/security/advisories/GHSA-rrvg-cxh4-qhrv
- https://nvd.nist.gov/vuln/detail/CVE-2026-33175
- https://github.com/jupyterhub/oauthenticator/commit/f0c7002dc36e41efae0f674033cf7888a21d96f9
- https://github.com/jupyterhub/oauthenticator
- https://github.com/jupyterhub/oauthenticator/releases/tag/17.4.0
- https://support.auth0.com/center/s/article/Enforce-Email-Verification-With-Sending-Email-After-Each-Denied-Access
