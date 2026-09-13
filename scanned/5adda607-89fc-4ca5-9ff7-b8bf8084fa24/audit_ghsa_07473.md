# [M] Sylius Mollie Plugin has unauthenticated IDOR that leaks order token and customer PII

## Summary
Severity: Medium
Advisory: GHSA-x83g-979r-f5fh
CVE: CVE-2026-68501
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-x83g-979r-f5fh
Type: github-advisory

## Affected
- Packagist: `sylius/mollie-plugin` — affected >=0 <2.2.8
- Packagist: `sylius/mollie-plugin` — affected >=3.0.0 <3.2.4
- Packagist: `sylius/mollie-plugin` — affected >=3.3.0 <3.3.1

## Details
### Impact
Two unauthenticated Mollie shop endpoints look up orders by a sequential integer `orderId`
with no ownership or session check. Chained, they expose customer PII.

`GET /{_locale}/thank-you` (`PageRedirectController::thankYouAction`, route
`sylius_mollie_shop_thank_you_page_redirect`) loads the order with `findOneBy(['id' => $orderId])`
and returns a `302` whose `Location` header carries that order's `tokenValue`. Any `orderId`
thus yields that order's token. A non-existent id dereferences null and returns a `500`. The
handler also writes the raw `orderId` into the session.

`GET /{_locale}/get-code` (`QrCodeAction::fetchQrCodeFromOrder`, route
`sylius_mollie_shop_get_qr_code`) runs the same lookup and returns the order's QR code and id
as JSON, ignoring the session cart; this is where the front-end got the integer id. A bad id
`500`s here too.

That `tokenValue` is the order's only access control. Passed to the Sylius core page
`GET /{_locale}/register-after-checkout/{tokenValue}` it returns a form pre-filled with the
customer's first name, last name and email. The full attack: enumerate `orderId`, read the
token from the redirect, read the PII, at roughly a 1-in-71 hit rate for guest orders.
`register-after-checkout` is Sylius core, not the plugin, and trusts the token by design, so
the leak is what must be fixed.

None of the plugin endpoints require a login, session or CSRF token.

### Patches
Fixed in **2.2.8**, **3.2.4** and **3.3.1**. 

### Workarounds
If you cannot upgrade immediately, patch both endpoints at the project level by decorating
the plugin controllers. The decorators enforce ownership before delegating to the original
controller, so no plugin behaviour is lost. They keep the original `orderId` request contract,
so no front-end or asset changes are required. Works on both 2.2 and 3.x.

#### Step 1. Decorate the QR code controller
Create `src/Controller/Mollie/SecureQrCodeAction.php` in your Sylius project:

```php
<?php

declare(strict_types=1);

namespace App\Controller\Mollie;

use Sylius\Component\Order\Context\CartContextInterface;
use Sylius\Component\Order\Context\CartNotFoundException;
use Sylius\MolliePlugin\Controller\Shop\QrCodeAction;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

final class SecureQrCodeAction
{
    private const OWNED_ORDER_IDS_SESSION_KEY = 'sylius_mollie.owned_order_ids';

    public function __construct(
        private readonly QrCodeAction $inner,
        private readonly CartContextInterface $cartContext,
    ) {
    }

    public function fetchQrCodeFromOrder(Request $request): JsonResponse
    {
        $orderId = $request->get('orderId');

        try {
            $cart = $this->cartContext->getCart();
        } catch (CartNotFoundException) {
            $cart = null;
        }

        if (null !== $orderId && (null === $cart || (string) $cart->getId() !== (string) $orderId)) {
            return new JsonResponse([], Response::HTTP_FORBIDDEN);
        }

        if (null !== $cart && null !== $cart->getId() && $request->hasSession()) {
            $session = $request->getSession();
            $ownedIds = $session->get(self::OWNED_ORDER_IDS_SESSION_KEY, []);
            $ownedIds[(string) $cart->getId()] = true;
            $session->set(self::OWNED_ORDER_IDS_SESSION_KEY, $ownedIds);
        }

        return $this->inner->fetchQrCodeFromOrder($request);
    }

    public function createPayment(Request $request): Response
    {
        return $this->inner->createPayment($request);
    }

    public function removeQrCodeFromOrder(Request $request): JsonResponse
    {
        return $this->inner->removeQrCodeFromOrder($request);
    }
}
```

#### Step 2. Decorate the thank-you controller
Create `src/Controller/Mollie/SecurePageRedirectController.php`:

```php
<?php

declare(strict_types=1);

namespace App\Controller\Mollie;

use Sylius\MolliePlugin\Controller\Shop\PageRedirectController;
use Symfony\Component\HttpFoundation\RedirectResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Session\SessionInterface;
use Symfony\Component\Routing\RouterInterface;

final class SecurePageRedirectController
{
    private const OWNED_ORDER_IDS_SESSION_KEY = 'sylius_mollie.owned_order_ids';

    public function __construct(
        private readonly PageRedirectController $inner,
        private readonly RouterInterface $router,
    ) {
    }

    public function thankYouAction(Request $request, SessionInterface $session): RedirectResponse
    {
        $orderId = $request->get('orderId');

        if (null !== $orderId) {
            $ownedIds = $session->get(self::OWNED_ORDER_IDS_SESSION_KEY, []);

            if (!isset($ownedIds[(string) $orderId])) {
                return new RedirectResponse($this->router->generate('sylius_shop_cart_summary'));
            }
        }

        return $this->inner->thankYouAction($request, $session);
    }
}
```

#### Step 3. Register the decorators
Append to your project's `config/services.yaml`:

```yaml
services:
    App\Controller\Mollie\SecureQrCodeAction:
        decorates: sylius_mollie.controller.shop.qr_code
        public: true
        arguments:
            $inner: '@.inner'
            $cartContext: '@sylius.context.cart'

    App\Controller\Mollie\SecurePageRedirectController:
        decorates: sylius_mollie.controller.shop.page_redirect
        public: true
        arguments:
            $inner: '@.inner'
            $router: '@router'
```

> Both decorators keep `@.inner` and only add an ownership check on `orderId` before handing
> the request to the original action, so `createPayment`, `removeQrCodeFromOrder` and the
> thank-you redirect all keep their original behaviour and the front-end contract is unchanged.

#### Step 4. Clear the cache
```bash
bin/console cache:clear
```

## References
- https://github.com/Sylius/MolliePlugin/security/advisories/GHSA-x83g-979r-f5fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-68501
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
