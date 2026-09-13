# [M] Admidio: Event participation IDOR - non-leaders can register other users for events via user_uuid parameter

## Summary
Severity: Medium
Advisory: GHSA-7pfv-hr63-h7cw
CVE: CVE-2026-30927
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2026-03-09
Source: https://github.com/advisories/GHSA-7pfv-hr63-h7cw
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.6

## Details
## Vulnerability

In `modules/events/events_function.php`, the event participation logic allows any user who can participate in an event to register OTHER users by manipulating the `user_uuid` GET parameter.

Line 47: `$getUserUuid = admFuncVariableIsValid($_GET, 'user_uuid', 'uuid', ...)`
Line 424: `if ($event->possibleToParticipate() || $participants->isLeader($gCurrentUserId))`

The condition uses `||` (OR), meaning if `possibleToParticipate()` returns true (event is open for participation), ANY user - not just leaders - can specify a different `user_uuid` and register/cancel participation for that user.

The code then operates on `$user->getValue('usr_id')` (the target user from user_uuid) rather than the current user.

## Impact
- Register unwilling users for events (potential harassment/spam)
- Cancel other users' event participation
- Manipulate event participant counts and comments
- If events have participation limits, fill slots with unwanted registrations

## Fix
For non-leader users, force `user_uuid` to the current user:
```php
if (!$participants->isLeader($gCurrentUserId)) {
    $getUserUuid = $gCurrentUser->getValue('usr_uuid');
}
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-7pfv-hr63-h7cw
- https://nvd.nist.gov/vuln/detail/CVE-2026-30927
- https://github.com/Admidio/admidio/issues/1985
- https://github.com/Admidio/admidio/commit/e47f70cc3cbcdb39635fdbaaef02d19f604b8c3e
- https://github.com/Admidio/admidio
