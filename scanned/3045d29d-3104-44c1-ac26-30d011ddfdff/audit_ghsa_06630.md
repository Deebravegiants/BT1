# [H] Sylius Mollie Plugin vulnerable to payment status forgery via the payment webhook

## Summary
Severity: High
Advisory: GHSA-rc52-c4hv-w89p
CVE: CVE-2026-68500
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-rc52-c4hv-w89p
Type: github-advisory

## Affected
- Packagist: `sylius/mollie-plugin` — affected >=0 <2.2.8
- Packagist: `sylius/mollie-plugin` — affected >=3.0.0 <3.2.4
- Packagist: `sylius/mollie-plugin` — affected >=3.3.0 <3.3.1

## Details
### Impact
  The shop payment webhook `POST /{_locale}/update-payment` (route
  `sylius_mollie_shop_payment_webhook`) accepts two independent, attacker-controlled
  parameters: `id` (the Mollie payment ID, verified against Mollie's API) and `orderId` (the
  Sylius order ID, read directly from the database). The handler never verifies that the
  Mollie payment belongs to the referenced order.

  An unauthenticated attacker who holds any valid **paid** Mollie payment ID, for example
  from a EUR 1 order they placed themselves, can submit it together with any victim
  `orderId`. The victim's order payment is then transitioned to `completed` (or any other
  Mollie-derived state) without any funds being transferred for that order. Sylius order IDs
  are sequential integers, and the endpoint requires no authentication, CSRF token or rate
  limiting, so the attack scales trivially across all pending orders.
  
  ### Patches
  Fixed in versions **2.2.8**, **3.2.4** and **3.3.1**. The webhook now binds the payment to
  the order: it reads the Mollie payment ID stored server-side for that order when the payment
  was created and compares it to the incoming Mollie payment ID. On mismatch the request is
  acknowledged with `HTTP 200` and no state change is applied. `HTTP 200` is intentional,
  because Mollie retries the webhook on any non-2xx response.

  The stored ID lives in one of two places depending on the checkout flow, and the fix reads
  both of them (mirroring `CaptureAction`):
  
  - `payment.getDetails()['payment_mollie_id']` for the standard Shop API and Apple Pay Direct
    flows, stored in `CreatePaymentAction`.
  - `order.getMolliePaymentId()` for the QR-code flow, which stores the ID on the order itself
    (`QrCodeAction`).

  Reading only the payment details would reject legitimate QR-code payments, because their
  payment details carry no `payment_mollie_id`, so both sources must be consulted.

  ### Workarounds
  If you cannot upgrade immediately, patch the vulnerability at the project level by
  decorating the plugin's webhook controller. The decorator checks that the incoming Mollie
  id matches the id stored for that order **before** handing over to the original controller,
  so no plugin behaviour (state machine, logging) is lost and no extra Mollie API call is
  made. Works on both 2.2 and 3.x.

  #### Step 1. Create the decorator
  Create `src/Controller/Mollie/SecurePaymentWebhookController.php` in your Sylius project:

  ```php
  <?php

  declare(strict_types=1);

  namespace App\Controller\Mollie;

  use Sylius\Component\Core\Model\OrderInterface;
  use Sylius\Component\Order\Repository\OrderRepositoryInterface;
  use Sylius\MolliePlugin\Controller\Shop\PaymentWebhookController;
  use Symfony\Component\HttpFoundation\JsonResponse;
  use Symfony\Component\HttpFoundation\Request;
  use Symfony\Component\HttpFoundation\Response;

  final class SecurePaymentWebhookController
  {
      public function __construct(
          private readonly PaymentWebhookController $inner,
          private readonly OrderRepositoryInterface $orderRepository,
      ) {
      }

      public function __invoke(Request $request): Response
      {
          $orderId = $request->get('orderId');
          $molliePaymentId = $request->get('id');

          if (null === $orderId || null === $molliePaymentId) {
              return ($this->inner)($request);
          }

          /** @var OrderInterface|null $order */
          $order = $this->orderRepository->findOneBy(['id' => $orderId]);
          if (null === $order) {
              return ($this->inner)($request);
          }

          $storedMollieId = $this->resolveStoredMollieId($order);
  
          // Reject any webhook whose Mollie id does not match the one stored for this order.
          // 200 is intentional: Mollie retries on any non-2xx response.
          if (null === $storedMollieId || $storedMollieId !== (string) $molliePaymentId) {
              return new JsonResponse(null, Response::HTTP_OK);
          }

          return ($this->inner)($request);
      }

      private function resolveStoredMollieId(OrderInterface $order): ?string
      {
          $payment = $order->getLastPayment();
          $fromDetails = $payment?->getDetails()['payment_mollie_id'] ?? null;
          if (null !== $fromDetails && '' !== $fromDetails) {
              return (string) $fromDetails;
          }
  
          // QR-code flow stores the Mollie id on the order itself.
          if (method_exists($order, 'getMolliePaymentId')) {
              $fromOrder = $order->getMolliePaymentId();
              if (null !== $fromOrder && '' !== $fromOrder) {
                  return (string) $fromOrder;
              }
          }
  
          return null;
      }
  }
  ```

  #### Step 2. Register the decorator
  Append to your project's `config/services.yaml`:

  ```yaml
  services:
      App\Controller\Mollie\SecurePaymentWebhookController:
          decorates: sylius_mollie.controller.shop.payment_webhook
          public: true
          arguments:
              $inner: '@.inner'
              $orderRepository: '@sylius.repository.order'
  ```

  > `decorates:` keeps the original service ID, so the route
  > `_controller: sylius_mollie.controller.shop.payment_webhook` keeps working with no route
  > changes. `@.inner` is the original plugin controller.

  #### Step 3. Clear the cache
  ```bash
  bin/console cache:clear
  ```

## References
- https://github.com/Sylius/MolliePlugin/security/advisories/GHSA-rc52-c4hv-w89p
- https://nvd.nist.gov/vuln/detail/CVE-2026-68500
- https://github.com/Sylius/MolliePlugin/pull/351
- https://github.com/Sylius/MolliePlugin/pull/352
- https://github.com/Sylius/MolliePlugin/pull/354
- https://github.com/Sylius/MolliePlugin/commit/01316b3ad3cf82e3c5ad160115d0a2cf89174e49
- https://github.com/Sylius/MolliePlugin/commit/153c754486b1bc597b67a90ac07ef71cd7958267
- https://github.com/Sylius/MolliePlugin/commit/d1f7753e92106e8bf3bedcfc61b02ea7b8e1c38a
- https://github.com/Sylius/MolliePlugin
- https://github.com/Sylius/MolliePlugin/releases/tag/v2.2.8
- https://github.com/Sylius/MolliePlugin/releases/tag/v3.2.4
- https://github.com/Sylius/MolliePlugin/releases/tag/v3.3.1
