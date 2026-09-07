# [H] YesWiki has Authenticated SQL Injection via ReactionManager 

## Summary
Severity: High
Advisory: GHSA-4pf7-cc4r-g63h
CVE: CVE-2026-52775
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-4pf7-cc4r-g63h
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.6.6

## Details
## Summary

YesWiki through the latest development branch contains a SQL injection vulnerability in `ReactionManager::deleteUserReaction()` that allows any authenticated user to inject arbitrary SQL via the `{idreaction}` and `{id}` URL path parameters. The parameters are concatenated directly into a SQL LIKE clause without escaping or parameterization.

This is a sibling of CVE-2026-46670 (unauthenticated SQLi in `FormManager::create()`). Both share the same root cause — raw string concatenation into SQL queries — but exist in different components.

## Root Cause

`includes/controllers/ApiController.php` line 726:
```php
/**
 * @Route("/api/reactions/{idreaction}/{id}/{page}/{username}", methods={"DELETE"}, options={"acl":{"+"}})
 */
```

ACL `"+"` = any authenticated user. Parameters flow into `ReactionManager::deleteUserReaction()` → `TripleStore::delete()` with raw string concatenation into SQL LIKE clause (line 356).

The `if` branch (lines 340-354) properly uses `$this->dbService->escape()`. The `else` branch does not — the developer applied escaping to one code path but not the other.

## PoC

```
DELETE /wiki/?api/reactions/x%27%20OR%201=1%20OR%20value%20LIKE%20%27/test/SomePage/attacker
Host: localhost:8085
Cookie: <session cookie>
```

Time-based blind variant via `{id}` parameter for data exfiltration.

## Impact

Full database read/write. Any self-registered user can extract `yeswiki_users` password hashes and emails.

## Suggested Fix

Apply `$this->dbService->escape()` to all parameters in the `else` branch, matching the `if` branch pattern. Also audit all `TripleStore::delete()` callers that pass `$extraSQL`.

## Credits

Kai Aizen / SnailSploit

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-4pf7-cc4r-g63h
- https://github.com/YesWiki/yeswiki/commit/90ca54fb518e1c43a1ead6e4f5bf9f0389789841
- https://github.com/YesWiki/yeswiki
