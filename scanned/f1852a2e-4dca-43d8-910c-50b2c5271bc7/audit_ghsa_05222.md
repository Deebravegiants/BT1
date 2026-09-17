# [H] WWBN AVideo: Authenticated wallet credit bypass in AuthorizeNet processPayment endpoint

## Summary
Severity: High
Advisory: GHSA-9392-pj54-qqf8
CVE: CVE-2026-47696
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-9392-pj54-qqf8
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
### Summary

  `plugin/AuthorizeNet/processPayment.json.php` credits the logged-in user's wallet based only on the attacker-controlled `amount` POST parameter.

  The endpoint contains a TODO for real Authorize.Net charging, hardcodes `$paymentSuccess = true`, and then calls `YPTWallet::addBalance()` without validating
  any Authorize.Net transaction, webhook signature, hosted payment token, nonce, or server-side payment record.

  This allows any logged-in user to add arbitrary funds to their own AVideo wallet when the `AuthorizeNet` and `YPTWallet` plugins are enabled.

  ### Details

  Affected file:

  `plugin/AuthorizeNet/processPayment.json.php`

  Relevant code:

  ```php
  $amount = isset($_POST['amount']) ? floatval($_POST['amount']) : 0;
  $userData = isset($_POST['userData']) ? $_POST['userData'] : [];

  if ($amount <= 0) {
      echo json_encode(['error' => 'Invalid amount']);
      exit;
  }

  // TODO: Implement payment logic using Authorize.Net API
  // Example: Call Authorize.Net API here
  // $result = $plugin->chargePayment($amount, $userData);

  // Simulate payment success for now
  $paymentSuccess = true;
  $users_id = @User::getId();

  if ($paymentSuccess && !empty($users_id)) {
      $walletPlugin = AVideoPlugin::loadPluginIfEnabled("YPTWallet");
      if ($walletPlugin) {
          $walletPlugin->addBalance($users_id, $amount, 'Authorize.Net one-time payment');
          echo json_encode(['success' => true, 'result' => 'Payment processed and wallet updated']);
          exit;
      }
  }
```
  Vulnerable flow:

  1. `$_POST['amount']` is read from the client.
  2. The endpoint only checks that the amount is greater than zero.
  3. The real Authorize.Net charge is not performed.
  4. `$paymentSuccess` is hardcoded to true.
  5. The logged-in user's wallet is credited with the client-supplied amount.

  There is no verification of:

  - Authorize.Net transaction ID
  - payment token
  - webhook signature
  - pending payment record
  - expected server-side amount
  - currency
  - duplicate transaction/replay state

  ### PoC

  Prerequisites:

  - AVideo with AuthorizeNet plugin enabled
  - YPTWallet plugin enabled
  - Attacker has any valid user account

  Steps:

  1. Log in as a low-privileged user.
  2. Open the wallet page and record the current balance.
  3. Send the following request with the user's authenticated session cookie:
```
  curl -i -s -b 'PHPSESSID=<user_session>' \
    -X POST 'https://target.example/plugin/AuthorizeNet/processPayment.json.php' \
    --data 'amount=9999&userData[note]=poc'
```
  4. The endpoint returns:
```
  {"success":true,"result":"Payment processed and wallet updated"}
```
  5. Refresh the wallet page.
  6. The wallet balance is increased by 9999.

  No Authorize.Net hosted payment page, card payment, transaction confirmation, webhook, or server-side payment validation is required.

### Impact

  A normal authenticated user can mint arbitrary wallet balance.

  Depending on the target site's configuration, this may allow the attacker to:

  - purchase paid videos or subscriptions without payment
  - abuse any feature backed by YPTWallet
  - transfer fake funds to other users
  - manipulate accounting or payout-related workflows
  - bypass monetization controls

### Recommended fix

- Remove or disable `processPayment.json.php` if it is obsolete.
- Never credit wallet balance from client-supplied `amount` alone.
- Use the existing Authorize.Net hosted token / webhook / transaction reconciliation flow.
- Require a verified Authorize.Net transaction ID and server-side amount lookup before calling `addBalance()`.
- Add regression tests proving arbitrary POSTs cannot credit a wallet.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-9392-pj54-qqf8
- https://nvd.nist.gov/vuln/detail/CVE-2026-47696
- https://github.com/WWBN/AVideo/commit/822402444b4db4e9442779c8c789ffe5312b3627
- https://github.com/WWBN/AVideo
