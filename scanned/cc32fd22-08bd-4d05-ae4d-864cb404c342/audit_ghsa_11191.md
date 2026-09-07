# [H] AVideo has SQL Injection via Partial Prepared Statement — videos_id Concatenated Directly into Query

## Summary
Severity: High
Advisory: GHSA-fj74-qxj7-r3vc
CVE: CVE-2026-33767
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-fj74-qxj7-r3vc
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <26.0

## Details
### Summary

In `objects/like.php`, the `getLike()` method constructs a SQL query using a prepared statement placeholder (`?`) for `users_id` but directly concatenates `$this->videos_id` into the query string without parameterization. An attacker who can control the `videos_id` value (via a crafted request) can inject arbitrary SQL, bypassing the partial prepared-statement protection.

### Details

**File:** `objects/like.php`

**Vulnerable code:**
```php
$sql = "SELECT * FROM likes WHERE users_id = ? AND videos_id = ".$this->videos_id." LIMIT 1;";
$res = sqlDAL::readSql($sql, "i", [$this->users_id]);
```

The query mixes a parameterized placeholder for `users_id` with raw string concatenation for `videos_id`. The `$this->videos_id` value originates from user-supplied request input (typically a POST/GET parameter identifying the video being liked/disliked) and is not cast to integer or validated before being embedded in the SQL string.

All other queries in the same file correctly use `?` placeholders for both columns:
```php
// Correct pattern used elsewhere:
$sql = "SELECT count(*) as total FROM likes WHERE videos_id = ? AND like = 1";
```

The inconsistency means any attacker who can submit a like/dislike action with a crafted `videos_id` can inject SQL. Since like/dislike actions are typically available to any authenticated user, the attack surface is broad.

### PoC

An attacker sends a like request with an injected `videos_id`:
```
POST /objects/likeAjax.json.php
videos_id=1 UNION SELECT user,password,3,4,5,6,7,8 FROM users-- -
```

This causes the backend to execute:
```sql
SELECT * FROM likes WHERE users_id = 1 AND videos_id = 1 UNION SELECT user,password,3,4,5,6,7,8 FROM users-- - LIMIT 1;
```

Result: full database read — user credentials, emails, private content, and any other data accessible to the MySQL user.

### Impact

- **Severity:** High
- **Authentication required:** Yes (must be logged in to like a video), but all registered users qualify
- **Impact:** Full database read via UNION-based injection; potential for data modification or deletion depending on DB user privileges
- **Fix:** Replace the concatenation with a second `?` placeholder and pass `$this->videos_id` as a bound integer parameter

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-fj74-qxj7-r3vc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33767
- https://github.com/WWBN/AVideo/commit/0215d3c4f1ee748b8880254967b51784b8ac4080
- https://github.com/WWBN/AVideo
