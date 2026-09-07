# [M] Flask-Security-Too OAuth reauthentication freshness bypass via cross-   user OAuth identity acceptance

## Summary
Severity: Medium
Advisory: GHSA-97r5-pg8x-p63p
CVE: CVE-2026-46715
CWE: CWE-287
Ecosystem: PyPI
Published: 2026-05-22
Source: https://github.com/advisories/GHSA-97r5-pg8x-p63p
Type: github-advisory

## Affected
- PyPI: `Flask-Security-Too` — affected >=5.8.0 <5.8.1

## Details
### Summary

  Flask-Security-Too 5.8.0's OAuth reauthentication flow can mark a
  session as fresh after verifying an OAuth account that belongs to a
  different user.

  If an attacker can operate an already-authenticated but stale victim
  session, they can complete OAuth verification using their own OAuth
  identity. The victim session is then treated as recently
  reauthenticated, allowing freshness-protected account actions to
  proceed. This was reproduced against the built-in `/change-username`
  route.

  ### Details

  The issue is in the OAuth verification callback.

  `_oauth_response_common()` resolves the OAuth provider identity to a
  Flask-Security user:

  - `flask_security/oauth_glue.py:101-108`

  `oauth_verify_response()` then accepts any resolved user and updates
  the current session freshness timestamp:

  - `flask_security/oauth_glue.py:182-214`
  - `flask_security/oauth_glue.py:201-204`

  The missing check is that the OAuth-resolved user must match the
  current authenticated session user. In the failing case:

  - current session user: `victim@example.com`
  - OAuth verified user: `attacker@example.com`
  - session marked fresh: yes

  So the attacker is not logging in as the victim, but they are
  satisfying the victim session's reauthentication requirement with a
  different account.

  ### PoC

  Tested version:

  - `Flask-Security-Too 5.8.0`
  - tag `5.8.0`
  - commit `08288dff6907e413d848a16aaf43fc2c2b2a3b72`

 Used a minimal Flask app with:

  ```python
  SECURITY_OAUTH_ENABLE = True
  SECURITY_OAUTH_BUILTIN_PROVIDERS = ["github"]
  SECURITY_FRESHNESS = timedelta(seconds=1)
  SECURITY_FRESHNESS_GRACE_PERIOD = timedelta(seconds=0)
  SECURITY_USERNAME_ENABLE = True
  SECURITY_CHANGE_USERNAME = True

  The OAuth provider was replaced with a localhost mock provider
  returning attacker@example.com. This avoids hitting a live third-party
  provider while still exercising Flask-Security-Too's real OAuth
  verification handler.

  Reproduction steps:

  1. Log in as victim@example.com.
  2. Wait until the session is no longer fresh.
  3. Confirm POST /change-username is blocked with 401 and
     reauth_required=true.
  4. Start OAuth verification with POST /login/oauth-verify-start/
     github.
  5. Complete the callback with an OAuth identity for
     attacker@example.com.
  6. Confirm the session is still for victim@example.com, but fs_paa has
     been updated.
  7. Retry POST /change-username.
  8. The victim user's username is changed successfully.

  Observed result:

  {
    "pre_bypass_status": 401,
    "pre_bypass_reauth_required": true,
    "attacker_identity": "attacker@example.com",
    "oauth_verify_response_status": 302,
    "post_bypass_change_username_status": 200,
    "final_email": "victim@example.com",
    "final_username": "victimowned1777878574",
    "direct_impact_verified": true
  }

  Note: CSRF was disabled in the local harness only to keep the test
  focused on the reauthentication check. This is not a CSRF bypass
  report.

  This bypasses Flask-Security-Too's freshness/reauthentication
  boundary.

  Applications using OAuth verification together with freshness-
  protected account operations may allow a stale victim session to be
  refreshed using a different user's OAuth account. In my test, this
  allowed the victim account's username to be changed through Flask-
  Security-Too's built-in /change-username route.

  A likely fix is to reject OAuth verification unless the resolved OAuth
  user matches current_user before updating session["fs_paa"].

## References
- https://github.com/pallets-eco/flask-security/security/advisories/GHSA-97r5-pg8x-p63p
- https://github.com/pallets-eco/flask-security
