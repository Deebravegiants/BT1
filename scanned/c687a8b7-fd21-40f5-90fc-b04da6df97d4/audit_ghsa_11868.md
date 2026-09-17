# [H] Sylius affected by IDOR in Cart and Checkout LiveComponents

## Summary
Severity: High
Advisory: GHSA-2xc6-348p-c2x6
CVE: CVE-2026-31820
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-2xc6-348p-c2x6
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=2.0.0 <2.0.16
- Packagist: `sylius/sylius` — affected >=2.1.0 <2.1.12
- Packagist: `sylius/sylius` — affected >=2.2.0 <2.2.3

## Details
### Impact
An authenticated Insecure Direct Object Reference (IDOR) vulnerability exists in multiple shop LiveComponents due to unvalidated resource IDs accepted via `#[LiveArg]` parameters. Unlike props, which are protected by LiveComponent's `@checksum`, `args` are fully user-controlled - any action that accepts a resource ID via `#[LiveArg]` and loads it with `->find()` without ownership validation is vulnerable.

Checkout address **FormComponent** (`addressFieldUpdated` action): Accepts an `addressId` via `#[LiveArg]` and loads it without verifying ownership, exposing another user's first name, last name, company, phone number, street, city, postcode, and country.

Cart **WidgetComponent** (`refreshCart` action): Accepts a `cartId` via `#[LiveArg]` and loads any order directly from the repository, exposing order total and item count.

Cart **SummaryComponent** (`refreshCart` action): Accepts a `cartId` via `#[LiveArg]` and loads any order directly from the repository, exposing subtotal, discount, shipping cost, taxes (excluded and included), and order total.

Since `sylius_order` contains both active carts (`state=cart`) and completed orders (`state=new/fulfilled`) in the same ID space, the cart IDOR exposes data from all orders, not just active carts.

### Patches
The issue is fixed in versions: 2.0.16, 2.1.12, 2.2.3 and above.

### Workarounds

Override vulnerable LiveComponent classes at the project level to add authorization checks to `#[LiveArg]` parameters.

#### Step 1. Exclude component overrides from default autowiring

In `config/services.yaml`, add `Twig/Component` to the exclude list to prevent duplicate service registration:

```yaml
App\:
    resource: '../src/*'
    exclude: '../src/{Entity,Kernel.php,Twig/Components}'
```

#### Step 2. Override checkout address FormComponent

Create `src/Twig/Components/Checkout/Address/FormComponent.php`:

```php
<?php

declare(strict_types=1);

namespace App\Twig\Components\Checkout\Address;

use Sylius\Bundle\ShopBundle\Twig\Component\Checkout\Address\AddressBookComponent;
use Sylius\Bundle\UiBundle\Twig\Component\ResourceFormComponentTrait;
use Sylius\Bundle\UiBundle\Twig\Component\TemplatePropTrait;
use Sylius\Component\Core\Model\OrderInterface;
use Sylius\Component\Core\Model\ShopUserInterface;
use Sylius\Component\Core\Repository\AddressRepositoryInterface;
use Sylius\Component\Core\Repository\OrderRepositoryInterface;
use Sylius\Component\Customer\Context\CustomerContextInterface;
use Sylius\Component\User\Repository\UserRepositoryInterface;
use Symfony\Component\Form\FormFactoryInterface;
use Symfony\Component\Form\FormInterface;
use Symfony\UX\LiveComponent\Attribute\AsLiveComponent;
use Symfony\UX\LiveComponent\Attribute\LiveArg;
use Symfony\UX\LiveComponent\Attribute\LiveListener;
use Symfony\UX\LiveComponent\Attribute\LiveProp;
use Symfony\UX\LiveComponent\Attribute\PreReRender;

#[AsLiveComponent]
class FormComponent
{
    /** @use ResourceFormComponentTrait<OrderInterface> */
    use ResourceFormComponentTrait;
    use TemplatePropTrait;

    #[LiveProp]
    public bool $emailExists = false;

    /**
     * @param OrderRepositoryInterface<OrderInterface> $repository
     * @param UserRepositoryInterface<ShopUserInterface> $shopUserRepository
     */
    public function __construct(
        OrderRepositoryInterface $repository,
        FormFactoryInterface $formFactory,
        string $resourceClass,
        string $formClass,
        protected readonly CustomerContextInterface $customerContext,
        protected readonly UserRepositoryInterface $shopUserRepository,
        protected readonly AddressRepositoryInterface $addressRepository,
    ) {
        $this->initialize($repository, $formFactory, $resourceClass, $formClass);
    }

    #[PreReRender(priority: -100)]
    public function checkEmailExist(): void
    {
        $email = $this->formValues['customer']['email'] ?? null;
        if (null !== $email) {
            $this->emailExists = $this->shopUserRepository->findOneByEmail($email) !== null;
        }
    }

    #[LiveListener(AddressBookComponent::SYLIUS_SHOP_ADDRESS_UPDATED)]
    public function addressFieldUpdated(#[LiveArg] mixed $addressId, #[LiveArg] string $field): void
    {
        $customer = $this->customerContext->getCustomer();
        if (null === $customer) {
            return;
        }

        // Fix: findOneByCustomer instead of find — validates ownership
        $address = $this->addressRepository->findOneByCustomer((string) $addressId, $customer);
        if (null === $address) {
            return;
        }

        $newAddress = [];
        $newAddress['firstName'] = $address->getFirstName();
        $newAddress['lastName'] = $address->getLastName();
        $newAddress['phoneNumber'] = $address->getPhoneNumber();
        $newAddress['company'] = $address->getCompany();
        $newAddress['countryCode'] = $address->getCountryCode();
        if ($address->getProvinceCode() !== null) {
            $newAddress['provinceCode'] = $address->getProvinceCode();
        }
        if ($address->getProvinceName() !== null) {
            $newAddress['provinceName'] = $address->getProvinceName();
        }
        $newAddress['street'] = $address->getStreet();
        $newAddress['city'] = $address->getCity();
        $newAddress['postcode'] = $address->getPostcode();

        $this->formValues[$field] = $newAddress;
    }

    protected function instantiateForm(): FormInterface
    {
        return $this->formFactory->create(
            $this->formClass,
            $this->resource,
            ['customer' => $this->customerContext->getCustomer()],
        );
    }
}
```

#### Step 3. Override cart WidgetComponent

Create `src/Twig/Components/Cart/WidgetComponent.php`:

```php
<?php

declare(strict_types=1);

namespace App\Twig\Components\Cart;

use Sylius\Bundle\ShopBundle\Twig\Component\Cart\FormComponent;
use Sylius\Bundle\UiBundle\Twig\Component\ResourceLivePropTrait;
use Sylius\Bundle\UiBundle\Twig\Component\TemplatePropTrait;
use Sylius\Component\Core\Model\OrderInterface;
use Sylius\Component\Core\Repository\OrderRepositoryInterface;
use Sylius\Component\Order\Context\CartContextInterface;
use Sylius\Component\Order\Context\CartNotFoundException;
use Sylius\Resource\Model\ResourceInterface;
use Sylius\TwigHooks\LiveComponent\HookableLiveComponentTrait;
use Symfony\UX\LiveComponent\Attribute\AsLiveComponent;
use Symfony\UX\LiveComponent\Attribute\LiveArg;
use Symfony\UX\LiveComponent\Attribute\LiveListener;
use Symfony\UX\LiveComponent\Attribute\LiveProp;
use Symfony\UX\LiveComponent\DefaultActionTrait;
use Symfony\UX\TwigComponent\Attribute\PreMount;

#[AsLiveComponent]
class WidgetComponent
{
    use DefaultActionTrait;
    use HookableLiveComponentTrait;
    use TemplatePropTrait;

    /** @use ResourceLivePropTrait<OrderInterface> */
    use ResourceLivePropTrait;

    #[LiveProp(hydrateWith: 'hydrateResource', dehydrateWith: 'dehydrateResource')]
    public ?ResourceInterface $cart = null;

    public function __construct(
        protected readonly CartContextInterface $cartContext,
        OrderRepositoryInterface $orderRepository,
    ) {
        $this->initialize($orderRepository);
    }

    #[PreMount]
    public function initializeCart(): void
    {
        $this->cart = $this->getCart();
    }

    #[LiveListener(FormComponent::SYLIUS_SHOP_CART_CHANGED)]
    #[LiveListener(FormComponent::SYLIUS_SHOP_CART_CLEARED)]
    public function refreshCart(#[LiveArg] mixed $cartId = null): void
    {
        // Fix: ignore user-supplied cartId, always load from session
        $this->cart = $this->getCart();
    }

    private function getCart(): ?OrderInterface
    {
        try {
            return $this->cartContext->getCart();
        } catch (CartNotFoundException) {
            return null;
        }

       return $cart;
    }
}
```

#### Step 4. Override cart SummaryComponent

Create `src/Twig/Components/Cart/SummaryComponent.php`:

```php
<?php

declare(strict_types=1);

namespace App\Twig\Components\Cart;

use Sylius\Bundle\ShopBundle\Twig\Component\Cart\FormComponent;
use Sylius\Bundle\UiBundle\Twig\Component\ResourceLivePropTrait;
use Sylius\Bundle\UiBundle\Twig\Component\TemplatePropTrait;
use Sylius\Component\Core\Model\OrderInterface;
use Sylius\Component\Core\Repository\OrderRepositoryInterface;
use Sylius\Resource\Model\ResourceInterface;
use Sylius\TwigHooks\LiveComponent\HookableLiveComponentTrait;
use Symfony\UX\LiveComponent\Attribute\AsLiveComponent;
use Symfony\UX\LiveComponent\Attribute\LiveArg;
use Symfony\UX\LiveComponent\Attribute\LiveListener;
use Symfony\UX\LiveComponent\Attribute\LiveProp;
use Symfony\UX\LiveComponent\DefaultActionTrait;

#[AsLiveComponent]
class SummaryComponent
{
    use DefaultActionTrait;
    use HookableLiveComponentTrait;

    /** @use ResourceLivePropTrait<OrderInterface> */
    use ResourceLivePropTrait;
    use TemplatePropTrait;

    #[LiveProp(hydrateWith: 'hydrateResource', dehydrateWith: 'dehydrateResource')]
    public ?ResourceInterface $cart = null;

    /** @param OrderRepositoryInterface<OrderInterface> $orderRepository */
    public function __construct(OrderRepositoryInterface $orderRepository)
    {
        $this->initialize($orderRepository);
    }

    #[LiveListener(FormComponent::SYLIUS_SHOP_CART_CHANGED)]
    public function refreshCart(#[LiveArg] mixed $cartId): void
    {
        // Fix: ignore user-supplied cartId, reload from checksummed cart prop
        if ($this->cart === null) {
            return;
        }

        $this->cart = $this->hydrateResource($this->cart->getId());
    }
}
```

#### Step 5. Register overridden services

In `config/services.yaml`, add:

```yaml
    sylius_shop.twig.component.checkout.address.form:
        class: App\Twig\Components\Checkout\Address\FormComponent
        arguments:
            $repository: '@sylius.repository.order'
            $formFactory: '@form.factory'
            $resourceClass: '%sylius.model.order.class%'
            $formClass: 'Sylius\Bundle\ShopBundle\Form\Type\Checkout\AddressType'
            $customerContext: '@sylius.context.customer'
            $shopUserRepository: '@sylius.repository.shop_user'
            $addressRepository: '@sylius.repository.address'
        tags:
            - { name: 'sylius.live_component.shop', key: 'sylius_shop:checkout:address:form' }

    sylius_shop.twig.component.cart.widget:
        class: App\Twig\Components\Cart\WidgetComponent
        arguments:
            $cartContext: '@sylius.context.cart.composite'
            $orderRepository: '@sylius.repository.order'
        tags:
            - { name: 'sylius.live_component.shop', key: 'sylius_shop:cart:widget' }

    sylius_shop.twig.component.cart.summary:
        class: App\Twig\Components\Cart\SummaryComponent
        arguments:
            $orderRepository: '@sylius.repository.order'
        tags:
            - { name: 'sylius.live_component.shop', key: 'sylius_shop:cart:summary' }
```

#### Step 6. Clear cache

```bash
php bin/console cache:clear
```

### Reporters

We would like to extend our gratitude to the following individuals for their detailed reporting and responsible disclosure of this vulnerability:
- Peter Stöckli (@p-)
- Man Yue Mo (@m-y-mo)
- The [GitHub Security Lab](https://securitylab.github.com) team

### For more information
If you have any questions or comments about this advisory:

- Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues?q=sort%3Aupdated-desc+is%3Aissue+is%3Aopen)
- Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-2xc6-348p-c2x6
- https://nvd.nist.gov/vuln/detail/CVE-2026-31820
- https://github.com/Sylius/Sylius
