# [M] Sylius is Missing Authorization in API v2 Add Item Endpoint

## Summary
Severity: Medium
Advisory: GHSA-wjmg-4cq5-m8hg
CVE: CVE-2026-31821
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-wjmg-4cq5-m8hg
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=2.0.0 <2.0.16
- Packagist: `sylius/sylius` — affected >=2.1.0 <2.1.12
- Packagist: `sylius/sylius` — affected >=2.2.0 <2.2.3

## Details
### Impact
The `POST /api/v2/shop/orders/{tokenValue}/items` endpoint does not verify cart ownership. An unauthenticated attacker can add items to other registered customers' carts by knowing the cart `tokenValue`.

```
POST /api/v2/shop/orders/{tokenValue}/items
```

Other mutation endpoints (PUT, PATCH, DELETE) are **not affected**. API Platform loads the Order entity through the state provider for these operations, which triggers `VisitorBasedExtension` and returns 404 for unauthorized users.

An attacker who obtains a cart `tokenValue` can add arbitrary items to another customer's cart. The endpoint returns the full cart representation in the response (HTTP 201), potentially leaking:

- Customer email address
- Cart contents (products, quantities, prices)
- Address data (billing and shipping if set)
- Payment and shipment IDs
- Order totals and tax breakdown
- Checkout state

### Patches
The issue is fixed in versions: 2.0.16, 2.1.12, 2.2.3, and above.

### Workarounds
Add an ownership check in `AddItemToCartHandler` by injecting `UserContextInterface` and verifying the current user matches the cart owner before adding items.

#### Step 1. Patch the handler

Create new  `src/CommandHandler/Cart/AddItemToCartHandler.php`:

```php
<?php

declare(strict_types=1);

namespace App\CommandHandler\Cart;

use Sylius\Bundle\ApiBundle\Command\Cart\AddItemToCart;
use Sylius\Bundle\ApiBundle\Context\UserContextInterface;
use Sylius\Component\Core\Factory\CartItemFactoryInterface;
use Sylius\Component\Core\Model\OrderInterface;
use Sylius\Component\Core\Model\OrderItemInterface;
use Sylius\Component\Core\Model\ProductVariantInterface;
use Sylius\Component\Core\Model\ShopUserInterface;
use Sylius\Component\Core\Repository\OrderRepositoryInterface;
use Sylius\Component\Core\Repository\ProductVariantRepositoryInterface;
use Sylius\Component\Order\Modifier\OrderItemQuantityModifierInterface;
use Sylius\Component\Order\Modifier\OrderModifierInterface;
use Symfony\Component\HttpKernel\Exception\NotFoundHttpException;
use Symfony\Component\Messenger\Attribute\AsMessageHandler;

#[AsMessageHandler]
final readonly class AddItemToCartHandler
{
    public function __construct(
        private OrderRepositoryInterface $orderRepository,
        private ProductVariantRepositoryInterface $productVariantRepository,
        private OrderModifierInterface $orderModifier,
        private CartItemFactoryInterface $cartItemFactory,
        private OrderItemQuantityModifierInterface $orderItemQuantityModifier,
        private UserContextInterface $userContext,
    ) {
    }

    public function __invoke(AddItemToCart $addItemToCart): OrderInterface
    {
        /** @var ProductVariantInterface|null $productVariant */
        $productVariant = $this->productVariantRepository->findOneBy(['code' => $addItemToCart->productVariantCode]);

        if ($productVariant === null) {
            throw new \InvalidArgumentException('Product variant with given code has not been found.');
        }

        /** @var OrderInterface|null $cart */
        $cart = $this->orderRepository->findCartByTokenValue($addItemToCart->orderTokenValue);

        if ($cart === null) {
            throw new \InvalidArgumentException('Cart with given token has not been found.');
        }

        $this->assertCartAccessible($cart);

        /** @var OrderItemInterface $cartItem */
        $cartItem = $this->cartItemFactory->createNew();
        $cartItem->setVariant($productVariant);

        $this->orderItemQuantityModifier->modify($cartItem, $addItemToCart->quantity);
        $this->orderModifier->addToOrder($cart, $cartItem);

        return $cart;
    }

    private function assertCartAccessible(OrderInterface $cart): void
    {
        if ($cart->isCreatedByGuest()) {
            return;
        }

        $cartCustomer = $cart->getCustomer();

        if (null === $cartCustomer || null === $cartCustomer->getUser()) {
            return;
        }

        $currentUser = $this->userContext->getUser();

        if (
            $currentUser instanceof ShopUserInterface
            && $currentUser->getCustomer()?->getId() === $cartCustomer->getId()
        ) {
            return;
        }

        throw new NotFoundHttpException('Cart not found.');
    }
}
```

#### Step 2. Override the service

```diff
# config/services.yaml

services:
    App\:
        resource: '../src/*'
-       exclude: '../src/{Entity,Kernel.php}'                                                                         
+       exclude: '../src/{Entity,Kernel.php,CommandHandler}'

    sylius_api.command_handler.cart.add_item_to_cart:
        class: App\CommandHandler\Cart\AddItemToCartHandler
        arguments:
            $orderRepository: '@sylius.repository.order'
            $productVariantRepository: '@sylius.repository.product_variant'
            $orderModifier: '@sylius.modifier.order'
            $cartItemFactory: '@sylius.factory.order_item'
            $orderItemQuantityModifier: '@sylius.modifier.order_item_quantity'
            $userContext: '@Sylius\Bundle\ApiBundle\Context\UserContextInterface'
        tags:
            - { name: messenger.message_handler, bus: sylius.command_bus }
```

#### Step 3. Clear cache

```bash
bin/console cache:clear
```

### Reporters

We would like to extend our gratitude to the following individuals for their detailed reporting and responsible disclosure of this vulnerability:
- @rokorolov

### For more information
If you have any questions or comments about this advisory:

- Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues?q=sort%3Aupdated-desc+is%3Aissue+is%3Aopen)
- Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-wjmg-4cq5-m8hg
- https://nvd.nist.gov/vuln/detail/CVE-2026-31821
- https://github.com/Sylius/Sylius
