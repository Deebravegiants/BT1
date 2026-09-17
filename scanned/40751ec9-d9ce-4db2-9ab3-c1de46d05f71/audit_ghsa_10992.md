# [M] AVideo has Unauthenticated IDOR - Playlist Information Disclosure

## Summary
Severity: Medium
Advisory: GHSA-6w2r-cfpc-23r5
CVE: CVE-2026-30885
CWE: CWE-306, CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-6w2r-cfpc-23r5
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <25.0

## Details
**Product:** AVideo (https://github.com/WWBN/AVideo)
**Version:** Latest (tested March 2026)
**Type:** Insecure Direct Object Reference (IDOR)
**Auth Required:** No
**User Interaction:** None

## Summary

The `/objects/playlistsFromUser.json.php` endpoint returns all playlists for any user without requiring authentication or authorization. An unauthenticated attacker can enumerate user IDs and retrieve playlist information including playlist names, video IDs, and playlist status for any user on the platform.

## Root Cause

The endpoint accepts a `users_id` parameter and directly queries the database without any authentication or authorization check.
**File:** `objects/playlistsFromUser.json.php`

```php
if (empty($_GET['users_id'])) {
    die("You need a user");
}
// NO AUTHENTICATION CHECK
// NO AUTHORIZATION CHECK (does this user_id belong to the requester?)
$row = PlayList::getAllFromUser($_GET['users_id'], false);
echo json_encode($row);
```

There is no call to `User::isLogged()` or any comparison between the requesting user and the target `users_id`.

## Affected Code

| File | Line | Issue |
|------|------|-------|
| `objects/playlistsFromUser.json.php` | 10-21 | No authentication or authorization check before returning playlist data |

## Proof of Concept

### Retrieve admin's playlists (user ID 1)

```bash
curl "https://TARGET/objects/playlistsFromUser.json.php?users_id=1"
```

**Response:**
```json
[
  {"id":false,"name":"Watch Later","status":"watch_later","users_id":1},
  {"id":false,"name":"Favorite","status":"favorite","users_id":1}
]
```

<img width="1805" height="365" alt="image" src="https://github.com/user-attachments/assets/a13c9c2f-29be-4399-98d2-7570ca30465a" />


## Impact

- **Privacy violation** — any visitor can see all users' playlist names and contents
- **User enumeration** — valid user IDs can be discovered by iterating through IDs
- **Information gathering** — playlist names and video IDs reveal user interests and private content preferences
- **Targeted attacks** — gathered information can be used for social engineering or further exploitation

## Remediation

Add authentication and authorization checks:

```php
// Option 1: Require authentication + only own playlists
if (!User::isLogged()) {
    die(json_encode(['error' => 'Authentication required']));
}
if ($_GET['users_id'] != User::getId() && !User::isAdmin()) {
    die(json_encode(['error' => 'Access denied']));
}

// Option 2: If public playlists are intended, filter by visibility
$row = PlayList::getAllFromUser($_GET['users_id'], false, 'public');
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-6w2r-cfpc-23r5
- https://nvd.nist.gov/vuln/detail/CVE-2026-30885
- https://github.com/WWBN/AVideo/commit/12adc66913724736937a61130ae2779c299445ca
- https://github.com/WWBN/AVideo
