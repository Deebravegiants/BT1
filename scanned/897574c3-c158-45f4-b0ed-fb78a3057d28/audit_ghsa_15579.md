# [M] Ory Kratos's setting required_aal `highest_available` does not properly respect code + mfa credentials

## Summary
Severity: Medium
Advisory: GHSA-wc43-73w7-x2f5
CVE: CVE-2024-45042
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-26
Source: https://github.com/advisories/GHSA-wc43-73w7-x2f5
Type: github-advisory

## Affected
- Go: `github.com/ory/kratos` — affected >=0 <1.3.0

## Details
## Preconditions

- The `code` login method is enabled with the `passwordless_enabled` flag set to `true` .
- A 2FA method such as `totp` is enabled.
- `required_aal` of the whomai check or the settings flow is set to `highest_available`. AAL stands for Authenticator Assurance Levels and can range from 0 (no factor) to 2 (two factors).
- A user uses the `code` method as the **only** login method available. They do not have a password or any other first factor credential enabled.
- The user has 2FA enabled.
- The user’s `available_aal` is incorrectly stored in the database as `aal1` or `aal0` or `NULL`.
- A user signs in using the code method, but does not complete the 2FA challenge.

**Example server configuration**

Below you will find an vulnerable example configuration. Keep in mind that, for the account to be vulnerable, the account must have no first factor except the `code` method enabled plus a second factor.

```
selfservice:
  methods:
    code:
      # The `code` login method is enabled with the `passwordless_enabled` flag set to `true`
      passwordless_enabled: true
    totp:
      # 2FA method such as `totp` is enabled
      enabled: true
  flows:
    settings:
      # This is set
      required_aal: highest_available
session:
  whoami:
    # Or this
    required_aal: highest_available
```

## Impact

Given the preconditions, the `highest_available` setting will incorrectly assume that the identity’s highest available AAL is `aal1` even though it really is `aal2`. This means that the `highest_available` configuration will act as if the user has only one factor set up, for that particular user. This means that they can call the settings and whoami endpoint without a `aal2` session, even though that should be disallowed.

An attacker would need to steal or guess a valid login OTP of a user who has only OTP for login enabled and who has an incorrect `available_aal` value stored, to exploit this vulnerability.

All other aspects of the session (e.g. the session’s aal) are not impacted by this issue.

On Ory Network, only 0,00066% of registered users were affected by this issue, and most of those users appeared to be test users. Their respective AAL values have since been updated and they are no longer vulnerable to this attack.

### Patches

Version 1.3.0 is not affected by this issue.

### Workarounds

If you require 2FA please disable the passwordless code login method. If that is not possible, check the sessions `aal` to identify if the user has `aal1` or `aal2`.

## References
- https://github.com/ory/kratos/security/advisories/GHSA-wc43-73w7-x2f5
- https://nvd.nist.gov/vuln/detail/CVE-2024-45042
- https://github.com/ory/kratos
