# [M] Shopware: Admin API ACL Bypass in Order State Transition Endpoints

## Summary
Severity: Medium
Advisory: GHSA-f8q6-3g5w-jjr6
CVE: CVE-2026-48014
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-f8q6-3g5w-jjr6
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.18
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.18

## Details
## Summary
This is a vertical authorization bypass in the Admin API affecting order state transition features (`/api/_action/order/{orderId}/state/{transition}` and similar transaction/delivery transition routes). The root cause is that the transition action routes do not declare required server-side ACL privileges, allowing low-privileged users to pass the authorization boundary. As a result, authenticated users without `order:update` can still change order states, causing real security impact such as operational integrity loss, automation workflow misuse, and fulfillment/settlement/support process disruption.

## Description
Shopware’s permission model requires server-side enforcement independent of UI guards. However, the dedicated order-state transition action endpoints are missing ACL metadata, so accounts without regular order update privileges can still submit transition requests that are processed by the backend. In real reproduction, the same low-privileged account receives 403 on the normal order update API, while the transition action API succeeds with 200 and updates order state in the database. The key point is that reproduction is possible through direct API calls regardless of UI access restrictions or hidden buttons. This is not a functional edge case; it is an implementation gap in authorization boundaries that enables privilege escalation behavior where a “read/limited-edit” user can control order lifecycle states.

### Expected Behavior
- Order, order-transaction, and order-delivery transition endpoints must perform explicit server-side ACL checks.
- Requests should be rejected unless the caller has the proper entity update privileges, such as `order:update`, `order_transaction:update`, or `order_delivery:update`.
- If an account gets 403 on the normal order update API, transition actions on the same protected resource should also be blocked by equivalent policy.
- Even if transition internals use SYSTEM_SCOPE, caller authorization must be validated before entering the transition execution path.

### Root Cause
File: `src/Core/Checkout/Order/Api/OrderActionController.php`

```php
#[Route(
    path: '/api/_action/order/{orderId}/state/{transition}',
    name: 'api.action.order.state_machine.order.transition_state',
    methods: [Request::METHOD_POST]
)]
public function orderStateTransition(
    string $orderId,
    string $transition,
    Request $request,
    Context $context
): JsonResponse {
    $toPlace = $this->orderService->orderStateTransition(
        $orderId,
        $transition,
        $request->request,
        $context
    );

    return new JsonResponse($toPlace->jsonSerialize());
}
```

This route exposes state transitions but forwards user-controlled inputs (`orderId`, `transition`) into the service layer without `PlatformRequest::ATTRIBUTE_ACL` and without an explicit `context->isAllowed(...)` privilege check. An untrusted caller can directly control the transition target.

File: `src/Core/Framework/Api/Acl/AclAnnotationValidator.php`

```php
$privileges = $request->attributes->get(PlatformRequest::ATTRIBUTE_ACL);

if (!$privileges) {
    return;
}
```

If route ACL metadata is absent, ACL validation exits immediately. Therefore these action routes skip authorization validation entirely.

File: `src/Core/System/StateMachine/StateMachineRegistry.php`

```php
public function transition(Transition $transition, Context $context): StateMachineStateCollection
{
    return $context->scope(Context::SYSTEM_SCOPE, function (Context $context) use ($transition): StateMachineStateCollection {
        // ...
        $this->stateMachineHistoryRepository->create([$stateMachineHistoryEntity], $context);
        $repository->upsert($data, $context);
        // ...
    });
}
```

Transitions run in SYSTEM_SCOPE and persist state/history with system context. This requires strict pre-authorization at the route/controller boundary, but that pre-check is missing, so low-privileged calls still lead to real state changes.

## Impact
The precondition is a remotely reachable authenticated low-privileged Admin API user (for example, operator/support account, or a compromised restricted account). The attacker only needs a valid order identifier, then calls transition action endpoints to cancel/reopen/advance order states without intended update privileges. This attack remains feasible even when UI access is restricted, because direct API calls still work. As a result, business workflows can be manipulated: order lifecycle integrity is broken, payment/shipping/document/notification/automation flows can be triggered incorrectly, and operational disruption can follow. In realistic scenarios, an attacker with a restricted account can mass-cancel or selectively alter orders, causing customer-support spikes, settlement inconsistencies, fulfillment mistakes, and practical availability degradation of day-to-day operations.

## Patch Recommendation
- Add explicit ACL requirements to order/order-transaction/order-delivery transition routes in `OrderActionController`, aligned with entity update privileges.
- Centralize server-side privilege checks at transition entry points so transition paths and normal update paths follow consistent authorization policy.
- Keep SYSTEM_SCOPE writes strictly behind authorization gates; ensure caller privilege decisions are completed in pre-check logic before transition execution.
- Review transition-related APIs to guarantee privilege model mapping (`order:*`, `order_transaction:*`, `order_delivery:*`) is consistently enforced and no unprotected route remains.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-f8q6-3g5w-jjr6
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.6.10.18
- https://github.com/shopware/shopware/releases/tag/v6.7.10.1
