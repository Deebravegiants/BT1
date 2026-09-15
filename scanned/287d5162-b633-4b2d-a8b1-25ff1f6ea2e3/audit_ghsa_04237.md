# [M] Hydro: Insufficient session expiration when recreating sessions

## Summary
Severity: Medium
Advisory: GHSA-94jp-7776-qj6q
CVE: CVE-2026-55617
CWE: CWE-613
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-94jp-7776-qj6q
Type: github-advisory

## Affected
- npm: `hydrooj` — affected >=4.10.4 <5.0.2

## Details
### Impact

Hydro contains an insufficient session expiration vulnerability in its session recreation logic. When a session is recreated, including during logout or other session renewal flows, Hydro creates a new session token but does not delete the previous server-side session token.

As a result, an old sid cookie may remain valid even after the legitimate user logs out or the session is recreated. An attacker who has obtained a victim's previous sid cookie can replay that cookie over HTTP or HTTPS and continue to access the affected Hydro instance as the victim.

The attacker does not need the victim's username or password. Exploitation requires possession of a previously valid stale sid cookie, but no user interaction is required at exploitation time.

Successful exploitation may allow account takeover within the affected Hydro instance. For a normal user account, this may allow disclosure of private data and unauthorized modification or deletion of data available to the victim.

### Patches

The issue has been patched by deleting the old server-side session token before creating a new one during session recreation.

Patched in:

- Pull request: https://github.com/hydro-dev/Hydro/pull/1173
- Patch commit: https://github.com/hydro-dev/Hydro/commit/8450390fcce5f7dc3f11c43a14f1d76dbb949a0d
- Merge commit: https://github.com/hydro-dev/Hydro/commit/8d76be8f0b83d911bf7671962b0467e9d4b5719a

Users should upgrade to a version containing this patch.

### Workarounds

If upgrading immediately is not possible, administrators should reduce the risk by forcing all existing sessions to expire or by clearing the server-side session token store after applying a local patch.

Administrators should also review logs for suspicious use of stale sid cookies and rotate any exposed session cookies. However, these mitigations do not fully fix the vulnerability. The recommended remediation is to upgrade to a patched version.

## References
- https://github.com/hydro-dev/Hydro/security/advisories/GHSA-94jp-7776-qj6q
- https://github.com/hydro-dev/Hydro/pull/1173
- https://github.com/hydro-dev/Hydro/commit/8450390fcce5f7dc3f11c43a14f1d76dbb949a0d
- https://github.com/hydro-dev/Hydro/commit/8d76be8f0b83d911bf7671962b0467e9d4b5719a
- https://github.com/hydro-dev/Hydro
