# [M] Shopware: Unauthorized Payment Trigger for Foreign Orders via /store-api/handle-payment

## Summary
Severity: Medium
Advisory: GHSA-9v5m-39wh-5chq
CVE: CVE-2026-48016
CWE: CWE-290
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-9v5m-39wh-5chq
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.18
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.18

## Details
## Summary

The Shopware Store API endpoint `/store-api/handle-payment` contains an object-level authorization flaw that allows a low-privileged external user with a normal customer or guest context to trigger the payment flow for another user’s order by supplying a foreign `orderId`. The affected functionality is the Store API payment initiation and retry flow. The root cause is that the endpoint forwards the user-controlled `orderId` into the payment processing logic without verifying that the caller owns the referenced order or has passed the required guest-order authentication. As a result, payment attempts for foreign orders are accepted by the server, which can compromise the integrity of order and payment workflows.

## Description

Shopware exposes `/store-api/handle-payment` to initiate or retry the payment flow for an already created order. Under the normal order access model, customers should only be able to view or act on their own orders, and guest users should only be able to access guest orders after completing additional verification such as `deepLinkCode`, email address, and postal code. The Store API `/store-api/order` route follows this model: authenticated customers only see their own orders, and guest users are denied access unless guest-order authentication is performed. However, `/store-api/handle-payment` does not follow the same protection model. It only checks whether the supplied `orderId` exists and then directly forwards it into the payment processing flow. As a result, an attacker who cannot read orders through the intended protected route can still trigger the payment retry or payment initiation logic for another customer’s order as long as they know a valid foreign order ID. Although `orderId` is a UUID-based identifier and is not trivially guessable, it is used throughout storefront order flows such as checkout finish, account order pages, payment change flows, and download links. It is therefore a business object identifier, not a secret bearer token. The server must not treat knowledge of a valid `orderId` as sufficient authorization and must instead verify that the caller is entitled to act on the referenced order. This is a backend authorization flaw caused by missing ownership validation on a sensitive order action.

### Expected Behavior

`/store-api/handle-payment` should only be available when the caller is the legitimate owner of the referenced order or, in the case of a guest order, when the required guest-order authentication has been completed. Before processing a supplied `orderId`, the server should verify that the current `SalesChannelContext` belongs to the customer associated with that order, or that the caller has successfully passed the expected guest-order verification flow. At a minimum, it should follow the same object-level authorization model used by the protected `/store-api/order` route.

### Root Cause

The vulnerable endpoint accepts `orderId`, checks only that the order exists and has a currency, and then forwards it into the payment processor without any ownership validation.

```php
#[Route(path: '/store-api/handle-payment', name: 'store-api.payment.handle', methods: ['GET', 'POST'])]
public function load(Request $request, SalesChannelContext $context): HandlePaymentMethodRouteResponse
{
    $data = [...$request->query->all(), ...$request->request->all()];
    $this->dataValidator->validate($data, $this->createDataValidation());
    /** @var array{orderId: string, finishUrl?: string, errorUrl?: string} $data */
    $orderCurrencyId = $this->getCurrencyFromOrder($data['orderId'], $context->getContext());

    if ($context->getCurrencyId() !== $orderCurrencyId) {
        $context = $this->contextService->get(
            new SalesChannelContextServiceParameters(
                $context->getSalesChannelId(),
                $context->getToken(),
                $context->getLanguageId(),
                $orderCurrencyId,
            )
        );
    }

    $response = $this->paymentProcessor->pay(
        $data['orderId'],
        $request,
        $context,
        $data['finishUrl'] ?? null,
        $data['errorUrl'] ?? null,
    );

    return new HandlePaymentMethodRouteResponse($response);
}
```

File: `src/Core/Checkout/Payment/SalesChannel/HandlePaymentMethodRoute.php`

The internal payment processing path similarly uses the supplied `orderId` to find the current transaction without checking whether the current caller owns the order.

```php
public function pay(
    string $orderId,
    Request $request,
    SalesChannelContext $salesChannelContext,
    ?string $finishUrl = null,
    ?string $errorUrl = null,
): ?RedirectResponse {
    $transaction = $this->getCurrentOrderTransaction($orderId, $salesChannelContext->getContext());
    if (!$transaction) {
        return null;
    }

    $response = $paymentHandler->pay($request, $transactionStruct, $salesChannelContext->getContext(), $validationStruct);

    return $response;
}

private function getCurrentOrderTransaction(string $orderId, Context $context): ?OrderTransactionEntity
{
    $criteria = (new Criteria())
        ->addFilter(new EqualsFilter('stateId', $this->initialStateIdLoader->get(OrderTransactionStates::STATE_MACHINE)))
        ->addFilter(new EqualsFilter('orderId', $orderId))
        ->addSorting(new FieldSorting('createdAt', FieldSorting::DESCENDING))
        ->setLimit(1);

    $transaction = $this->orderTransactionRepository->search($criteria, $context)->getEntities()->first();

    if (!$transaction) {
        $criteria->resetFilters();
        $criteria->addFilter(new EqualsFilter('orderId', $orderId));

        if ($this->orderTransactionRepository->searchIds($criteria, $context)->firstId()) {
            return null;
        }

        throw PaymentException::invalidOrder($orderId);
    }

    return $transaction;
}
```

File: `src/Core/Checkout/Payment/PaymentProcessor.php`

By contrast, the official order retrieval route explicitly enforces current-context order ownership.

```php
if ($context->getCustomer()) {
    $criteria->addFilter(new EqualsFilter('order.orderCustomer.customerId', $context->getCustomerId()));
} elseif ($deepLinkFilter === null) {
    throw OrderException::customerNotLoggedIn();
}

if ($deepLinkFilter !== null && !$context->getCustomer()) {
    $order = $orders->first();

    if ($order === null) {
        throw OrderException::guestNotAuthenticated();
    }

    $this->guestAuthenticator->validate($order, $request);
}
```

File: `src/Core/Checkout/Order/SalesChannel/OrderRoute.php`

The Store API schema also reflects that `/store-api/order` is designed for customer-owned or guest-authenticated order access, while `/store-api/handle-payment` only requires `orderId`.

```json
{
  "summary": "Fetch a list of orders",
  "description": "List orders of a customer."
}
```

File: `src/Core/Framework/Api/ApiDefinition/Generator/Schema/StoreApi/paths/order.json`

```json
{
  "summary": "Initiate a payment for an order",
  "required": ["orderId"]
}
```

File: `src/Core/Framework/Api/ApiDefinition/Generator/Schema/StoreApi/paths/handle-payment.json`

The expected model is that both order access and payment initiation are tied to order ownership or guest-order authentication. The implemented model instead trusts a caller-supplied `orderId` and allows a sensitive payment action on a foreign order.

## Impact

The attacker only needs to be a normal remote Store API user and does not need to be an authenticated backend user. Even a guest context is sufficient. No administrator privileges, backend access, shell access, or other special internal conditions are required. In a realistic scenario, an external user can create a normal guest Store API context through the storefront or Store API and then submit a valid foreign order ID learned through another channel to `/store-api/handle-payment` in order to trigger the payment retry or payment initiation flow for another customer’s order. Here, `orderId` should not be treated as a secret authorization token. While it is not trivially guessable, it is used throughout storefront order-related flows such as checkout finish, account order detail pages, payment update routes, and download links as a business object identifier. Treating possession of a valid `orderId` as sufficient authorization breaks the expectation that only the legitimate order owner, or a properly authenticated guest-order user, may perform payment-related follow-up actions. In practice, this can lead to unauthorized payment attempts, external payment integration calls, customer confusion, and disruption of order processing integrity. The primary impact is on the integrity of order and payment workflows, with potential secondary operational or availability impact depending on the payment integration.

## Patch Recommendation

Before processing a supplied `orderId`, `/store-api/handle-payment` should enforce the same object-level authorization model used by the order access routes. For authenticated customers, the server should verify that the order belongs to the current customer. For guest orders, it should require and validate the same guest-order authentication conditions used in the official order retrieval flow. In addition, the internal payment processor should not resolve a transaction solely by `orderId`; transaction lookup should be constrained to orders that are authorized for the current sales channel context and caller.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-9v5m-39wh-5chq
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.6.10.18
- https://github.com/shopware/shopware/releases/tag/v6.7.10.1
