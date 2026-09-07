# [M] AVideo: IDOR in PayPalYPT Plugin Allows Any Authenticated User to Cancel Arbitrary PayPal Subscription Agreements

## Summary
Severity: Medium
Advisory: GHSA-958h-qp3x-q4gj
CVE: CVE-2026-43883
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-958h-qp3x-q4gj
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

`plugin/PayPalYPT/agreementCancel.json.php` cancels a PayPal billing agreement using an attacker-supplied `agreement` parameter without verifying that the authenticated user owns the agreement. A low-privilege authenticated user who learns or obtains another user's PayPal billing agreement ID can silently suspend the victim's recurring subscription, causing revenue loss to the platform and loss of paid service to the victim.

## Details

AVideo's PayPalYPT plugin ships two near-duplicate endpoints that cancel a PayPal billing agreement. Only one of them enforces ownership:

- `plugin/PayPalYPT/PayPalAgreementCancel.json.php:19` — correctly requires either admin or the agreement's owner:
  ```php
  if (!User::isAdmin() && !Subscription::isAgreementFromUser($_POST['agreement_id'], User::getId())) {
      $obj->msg = "Only the owner can delete his agreement";
      die(json_encode($obj));
  }
  ```

- `plugin/PayPalYPT/agreementCancel.json.php:9-26` — only checks `User::isLogged()` (in fact twice, redundantly) and then calls the cancellation directly:

  ```php
  if (!User::isLogged()) { ... die; }              // line 9
  if (empty($_REQUEST['agreement'])) { ... die; }   // line 14
  if (!User::isLogged()) { ... die; }              // line 19 — duplicate; no ownership check
  $plugin = AVideoPlugin::loadPluginIfEnabled("PayPalYPT");
  $agreement = PayPalYPT::cancelAgreement($_REQUEST['agreement']);  // line 26
  ```

`PayPalYPT::cancelAgreement()` at `plugin/PayPalYPT/PayPalYPT.php:548-566` resolves the agreement ID against PayPal and calls `$createdAgreement->suspend($agreementStateDescriptor, $apiContext)` unconditionally — the server does not verify that the logged-in user's `users_id` matches the owner recorded in `PayPalYPT_log` (or wherever the agreement was registered):

```php
public static function cancelAgreement($agreement_id)
{
    ...
    $createdAgreement = self::getBillingAgreement($agreement_id);
    try {
        $createdAgreement->suspend($agreementStateDescriptor, $apiContext);
        return Agreement::get($createdAgreement->getId(), $apiContext);
    } catch (Exception $ex) {
        return false;
    }
}
```

The intended UI caller is `subscriptions_list.php:84` which posts the current user's own agreement IDs — but the server accepts any `agreement` parameter from any logged-in user. Agreement IDs can leak via `_error_log` entries written in `agreementCancel.json.php:34` and `webhook.php` during normal operation, via PayPal receipt emails, or via other administrative and payment-log screens. No CSRF token is required, but the root defect is missing authorization, not CSRF.

## PoC

1. Log in as any low-privilege user (registered subscriber, commenter, free-tier account created via `signUp`).
2. Obtain the target's PayPal agreement ID (e.g., `I-ABCD1234XYZ`). This may come from server error logs, email receipts, admin/payment screens, or other disclosures.
3. Send the request with the victim's agreement ID:

   ```bash
   curl -X POST 'https://target.example/plugin/PayPalYPT/agreementCancel.json.php' \
     -b 'PHPSESSID=<attacker_session>' \
     -d 'agreement=I-ABCD1234XYZ'
   ```

4. Expected response:
   ```json
   {"error":false,"msg":""}
   ```
   The victim's billing agreement is suspended at PayPal via `Agreement::suspend()` (PayPalYPT.php:560). The victim stops being billed; AVideo subsequently reflects the subscription as inactive.

## Impact

- Any authenticated user can silently cancel another user's active PayPal recurring billing agreement.
- Revenue disruption for the platform operator — any affected subscribers stop being billed.
- Service disruption for the victim — their paid subscription lapses.
- The defect is purely an authorization gap; the sister endpoint `PayPalAgreementCancel.json.php` demonstrates that the owner/admin check was intentional for this action but was not applied to this duplicate.

## Recommended Fix

Port the ownership check from the sister endpoint into `agreementCancel.json.php`:

```php
if (!User::isAdmin() && !Subscription::isAgreementFromUser($_REQUEST['agreement'], User::getId())) {
    $obj->msg = "Only the owner can cancel this agreement";
    die(json_encode($obj));
}
```

Alternative, preferred remediation: delete the duplicate `agreementCancel.json.php` entirely and point the `cancelAgreement()` JS helper in `subscriptions_list.php:84` at the already-protected `PayPalAgreementCancel.json.php` endpoint (sending the expected `agreement_id` POST field). While patching, also remove the redundant second `User::isLogged()` branch at line 19.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-958h-qp3x-q4gj
- https://nvd.nist.gov/vuln/detail/CVE-2026-43883
- https://github.com/WWBN/AVideo/commit/0da3dcff1eda2f497694bf82b559829471c292c2
- https://github.com/WWBN/AVideo
