# [C] Sentry's improper authentication on SAML SSO process allows user identity linking

## Summary
Severity: Critical
Advisory: GHSA-rcmw-7mc7-3rj7
CVE: CVE-2026-42354
CWE: CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-rcmw-7mc7-3rj7
Type: github-advisory

## Affected
- PyPI: `sentry` — affected >=21.12.0 <26.4.1

## Details
### Impact
A critical vulnerability was discovered in the SAML SSO implementation of Sentry. It was reported to us via Sentry's private bug bounty program.

The vulnerability allows an attacker to take over any user account by using a malicious SAML Identity Provider and another organization on the same Sentry instance. The victim email address must be known in order to exploit this vulnerability.

Self-hosted users are only vulnerable if the following conditions are met:
- They have more than one organization configured (SENTRY_SINGLE_ORGANIZATION = False).
- A malicious user has existing access and permissions to modify SSO settings for another organization in their multi-organization instance. 

### Patches
- [Sentry SaaS](https://sentry.io/): The fix was deployed in April. No action is required.
- [Self-Hosted Sentry](https://github.com/getsentry/self-hosted): If only a single organization is allowed (SENTRY_SINGLE_ORGANIZATION = True), then no action is needed. Sentry recommends upgrading to version 26.4.1 or higher.

### Workarounds
User account-based two-factor authentication prevents an attacker from being able to complete authentication with a victim's user account. Organization administrators cannot do this on a user's behalf, this requires individual users to ensure 2FA has been enabled for their account.

Users can manage their two-factor authentication settings through Account Settings > [Security](https://sentry.io/settings/account/security/) page. For step-by-step details, please see the Sentry [helpdesk article](https://sentry.zendesk.com/hc/en-us/articles/46773315774235-How-do-I-enable-two-factor-authentication-2FA-on-my-Sentry-account).

### Resources

- https://github.com/getsentry/sentry/pull/113720 

Please note that this is distinct vulnerability from the similar https://github.com/getsentry/sentry/security/advisories/GHSA-7pq6-v88g-wf3w from 2025.

## References
- https://github.com/getsentry/sentry/security/advisories/GHSA-rcmw-7mc7-3rj7
- https://nvd.nist.gov/vuln/detail/CVE-2026-42354
- https://github.com/getsentry/sentry/pull/113720
- https://github.com/getsentry/sentry/commit/0c67558ae7fe08738912d4c5233b53ead048da3b
- https://github.com/getsentry/sentry
- https://github.com/getsentry/sentry/releases/tag/26.4.1
