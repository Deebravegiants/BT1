# [M] khoj has an IDOR in subscription management allows unauthorized subscription modifications

## Summary
Severity: Medium
Advisory: GHSA-hq4h-w933-jm6c
CVE: CVE-2024-52294
CWE: CWE-639
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-12-30
Source: https://github.com/advisories/GHSA-hq4h-w933-jm6c
Type: github-advisory

## Affected
- PyPI: `khoj` — affected >=0 <1.29.0

## Details
### Summary
An Insecure Direct Object Reference (IDOR) vulnerability in the update_subscription endpoint allows any authenticated user to manipulate other users' Stripe subscriptions by simply modifying the email parameter in the request.

### Details
The vulnerability exists in the subscription endpoint at `/api/subscription`. The endpoint uses an email parameter as a direct reference to user subscriptions without verifying object ownership. While authentication is required, there is no authorization check to verify if the authenticated user owns the referenced subscription.

Vulnerable code in `/api/subscription`:
```python
@subscription_router.patch("")
@requires(["authenticated"])
async def update_subscription(request: Request, email: str, operation: str):
    # IDOR: email parameter directly references user subscriptions without ownership verification
    customers = stripe.Customer.list(email=email).auto_paging_iter()
    customer = next(customers, None)
    
    if operation == "cancel":
        # Any authenticated user can modify any subscription referenced by email
        customer_id = customer.id
        for subscription in stripe.Subscription.list(customer=customer_id):
            stripe.Subscription.modify(subscription.id, cancel_at_period_end=True)
```

### PoC
1. Create a customer account in stripe:
   - Customer A: `adventure8812@zeropath.com` (attacker)

2. Log in as any user.

3. Send this request:
```http
PATCH /api/subscription?email=adventure8812@zeropath.com&operation=cancel HTTP/1.1
```

4. The subscription for Customer A is successfully set to cancel.

### Impact
High:
Revenue loss via mass cancellation of subscriptions.
Loss of customer trust by re-enabling subscriptions they had set to cancel.

### Resolution

This was fixed in the following commit which limited subscription update operations to the authenticated user: https://github.com/khoj-ai/khoj/commit/47d3c8c23597900af708bdc60aced3ae5d2064c1. Support for arbitrarily presenting an email for update has been deprecated.

## References
- https://github.com/khoj-ai/khoj/security/advisories/GHSA-hq4h-w933-jm6c
- https://nvd.nist.gov/vuln/detail/CVE-2024-52294
- https://github.com/khoj-ai/khoj/commit/47d3c8c23597900af708bdc60aced3ae5d2064c1
- https://github.com/khoj-ai/khoj
