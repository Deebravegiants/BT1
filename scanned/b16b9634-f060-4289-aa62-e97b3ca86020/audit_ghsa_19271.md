# [M] Rack session gets restored after deletion

## Summary
Severity: Medium
Advisory: GHSA-9j94-67jr-4cqj
CVE: CVE-2025-46336
CWE: CWE-362, CWE-367, CWE-613
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-08
Source: https://github.com/advisories/GHSA-9j94-67jr-4cqj
Type: github-advisory

## Affected
- RubyGems: `rack-session` — affected >=2.0.0 <2.1.1

## Details
## Summary

When using the `Rack::Session::Pool` middleware, simultaneous rack requests can restore a deleted rack session, which allows the unauthenticated user to occupy that session.

## Details

[Rack session middleware](https://github.com/rack/rack-session/blob/v2.1.0/lib/rack/session/abstract/id.rb#L271-L278) prepares the session at the beginning of request, then saves is back to the store with possible changes applied by host rack application. This way the session becomes to be a subject of race conditions in general sense over concurrent rack requests.

## Impact

When using the `Rack::Session::Pool` middleware, and provided the attacker can acquire a session cookie (already a major issue), the session may be restored if the attacker can trigger a long running request (within that same session) adjacent to the user logging out, in order to retain illicit access even after a user has attempted to logout.

## Mitigation

- Update to the latest version of `rack-session`, or
- Ensure your application invalidates sessions atomically by marking them as logged out e.g., using a `logged_out` flag, instead of deleting them, and check this flag on every request to prevent reuse, or
- Implement a custom session store that tracks session invalidation timestamps and refuses to accept session data if the session was invalidated after the request began.

## Related

This code was previously part of `rack` in Rack < 3, see <https://github.com/rack/rack/security/advisories/GHSA-vpfw-47h7-xj4g> for the equivalent advisory in `rack` (affecting Rack < 3 only).

## References
- https://github.com/rack/rack-session/security/advisories/GHSA-9j94-67jr-4cqj
- https://github.com/rack/rack/security/advisories/GHSA-vpfw-47h7-xj4g
- https://nvd.nist.gov/vuln/detail/CVE-2025-46336
- https://github.com/rack/rack-session/commit/c28c4a8c1861d814e09f2ae48264ac4c40be2d3b
- https://github.com/rack/rack-session
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack-session/CVE-2025-46336.yml
