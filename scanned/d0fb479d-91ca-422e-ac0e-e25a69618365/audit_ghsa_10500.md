# [M] AVideo: Arbitrary Stripe Subscription Cancellation via Debug Endpoint and retrieveSubscriptions() Bug

## Summary
Severity: Medium
Advisory: GHSA-38rh-4v39-vfxv
CVE: CVE-2026-34737
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-38rh-4v39-vfxv
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The StripeYPT plugin includes a `test.php` debug endpoint that is accessible to any logged-in user, not just administrators. This endpoint processes Stripe webhook-style payloads and triggers subscription operations, including cancellation. Due to a bug in the `retrieveSubscriptions()` method that cancels subscriptions instead of merely retrieving them, any authenticated user can cancel arbitrary Stripe subscriptions by providing a subscription ID.

## Details

At `plugin/StripeYPT/test.php:4`, the endpoint checks only for a logged-in user, not for admin privileges:

```php
if (!User::isLogged())
```

At lines 27-29, the endpoint accepts a JSON payload from the request and processes it through the Stripe metadata handler:

```php
$obj = StripeYPT::getMetadataOrFromSubscription(json_decode($_REQUEST['payload']));
```

The call chain proceeds as follows:
- `test.php` calls `getMetadataOrFromSubscription()`
- Which calls `getSubscriptionId()` to extract the subscription ID
- Which calls `retrieveSubscriptions()` to interact with the Stripe API

At `StripeYPT.php:933`, the `retrieveSubscriptions()` method contains a critical bug where it cancels the subscription instead of just retrieving it:

```php
$response = $sub->cancel();
```

This same bug also affects the production webhook processing path via `processSubscriptionIPN()`, meaning both the debug endpoint and the live webhook handler can trigger unintended cancellations.

## Proof of Concept

1. Log in as any regular (non-admin) user and obtain a session cookie.

2. Send a crafted payload to the test endpoint with a target subscription ID:

```bash
curl -b "PHPSESSID=USER_SESSION" \
  "https://your-avideo-instance.com/plugin/StripeYPT/test.php" \
  -d 'payload={"data":{"object":{"id":"sub_TARGET_SUBSCRIPTION_ID","customer":"cus_CUSTOMER_ID"}}}'
```

3. The endpoint processes the payload, calls `retrieveSubscriptions()`, and the subscription is cancelled via the Stripe API.

4. To enumerate subscription IDs, check if the application exposes them through other endpoints or use predictable patterns:

```bash
# Check user subscription details if accessible
curl -b "PHPSESSID=USER_SESSION" \
  "https://your-avideo-instance.com/plugin/StripeYPT/listSubscriptions.php"
```

5. The Stripe subscription is now cancelled. The affected user loses access to their paid features.

## Impact

Any logged-in user can cancel arbitrary Stripe subscriptions belonging to other users. This causes direct financial damage to the platform operator (lost subscription revenue) and service disruption for paying subscribers who lose access to premium features. The debug endpoint should have been removed from production or restricted to admin-only access, and the `retrieveSubscriptions()` method should retrieve rather than cancel subscriptions.

- **CWE-862**: Missing Authorization
- **Severity**: Medium

## Recommended Fix

Two changes are needed:

**1. Restrict the debug endpoint to admins** at `plugin/StripeYPT/test.php:4`:

```php
// plugin/StripeYPT/test.php:4
if (!User::isAdmin())
```

Change `User::isLogged()` to `User::isAdmin()` so only administrators can access the debug endpoint.

**2. Fix the retrieval bug** at `StripeYPT.php:933`:

Remove the `$sub->cancel()` call from `retrieveSubscriptions()` so that the function only retrieves subscription data without cancelling it:

```php
// StripeYPT.php:933 - remove the following line:
// $response = $sub->cancel();
```

The `retrieveSubscriptions()` method should retrieve subscription information, not cancel subscriptions as a side effect.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-38rh-4v39-vfxv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34737
- https://github.com/WWBN/AVideo/commit/8ac79b9375872f02f72999157b19a40c17126513
- https://github.com/WWBN/AVideo
