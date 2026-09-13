# [M] Sylius: Channel-based payment method restriction bypass on shop account orders API endpoint

## Summary
Severity: Medium
Advisory: GHSA-6955-hrm5-c4qp
CVE: CVE-2026-53638
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-6955-hrm5-c4qp
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=2.0.0 <2.0.18
- Packagist: `sylius/sylius` — affected >=2.1.0 <2.1.15
- Packagist: `sylius/sylius` — affected >=2.2.0 <2.2.6

## Details
### Impact
An authorization bypass vulnerability exists in the shop account API. The `PATCH /api/v2/shop/account/orders/{tokenValue}/payments/{paymentId}` endpoint, used by an authenticated shop customer to change the payment method of an order that has been placed but not yet paid (state `STATE_NEW`), does not validate that the chosen payment method is enabled for the order's channel. The equivalent checkout endpoint (`PATCH /api/v2/shop/orders/{tokenValue}/payments/{paymentId}`) correctly rejects out-of-channel payment methods with `HTTP 422`; the account endpoint silently accepts them and returns `HTTP 200`.

An authenticated customer can therefore assign any globally enabled payment method to their own placed order, including methods that the store operator has explicitly excluded from that channel. 

### Patches
The issue is fixed in versions: 2.0.18, 2.1.15, 2.2.6 and above.

### Workarounds
If users cannot bump Sylius right now, decorate the `Sylius\Bundle\ApiBundle\Changer\PaymentMethodChangerInterface` service in their applications. 

#### Step 1. Create the decorator

`src/Decorator/ChannelCheckingPaymentMethodChanger.php`:

```php
<?php

declare(strict_types=1);

namespace App\Decorator;

use ApiPlatform\Validator\Exception\ValidationException;
use Sylius\Bundle\ApiBundle\Changer\PaymentMethodChangerInterface;
use Sylius\Component\Core\Model\OrderInterface;
use Sylius\Component\Core\Model\PaymentMethodInterface;
use Sylius\Component\Core\Repository\PaymentMethodRepositoryInterface;
use Sylius\Component\Core\Repository\PaymentRepositoryInterface;
use Sylius\Component\Payment\Resolver\PaymentMethodsResolverInterface;
use Symfony\Component\Validator\ConstraintViolation;
use Symfony\Component\Validator\ConstraintViolationList;
use Symfony\Contracts\Translation\TranslatorInterface;

final readonly class ChannelCheckingPaymentMethodChanger implements PaymentMethodChangerInterface
{
    public function __construct(
        private PaymentMethodChangerInterface $decorated,
        private PaymentRepositoryInterface $paymentRepository,
        private PaymentMethodRepositoryInterface $paymentMethodRepository,
        private PaymentMethodsResolverInterface $paymentMethodsResolver,
        private TranslatorInterface $translator,
    ) {
    }

    public function changePaymentMethod(string $paymentMethodCode, mixed $paymentId, OrderInterface $order): OrderInterface
    {
        /** @var PaymentMethodInterface|null $paymentMethod */
        $paymentMethod = $this->paymentMethodRepository->findOneBy(['code' => $paymentMethodCode]);
        $payment = $this->paymentRepository->findOneByOrderId($paymentId, $order->getId());

        if (
            $paymentMethod !== null
            && $payment !== null
            && !in_array($paymentMethod, $this->paymentMethodsResolver->getSupportedMethods($payment), true)
        ) {
            $template = 'sylius.payment_method.not_available';
            $parameters = ['%name%' => (string) $paymentMethod->getName()];

            throw new ValidationException(new ConstraintViolationList([
                new ConstraintViolation(
                    message: $this->translator->trans($template, $parameters, 'validators'),
                    messageTemplate: $template,
                    parameters: $parameters,
                    root: $paymentMethodCode,
                    propertyPath: '',
                    invalidValue: $paymentMethodCode,
                ),
            ]));
        }

        return $this->decorated->changePaymentMethod($paymentMethodCode, $paymentId, $order);
    }
}
```

#### Step 2. Register the decorator

`config/services.yaml` (append to the application's existing `services:` block):

```yaml
services:
    App\Decorator\ChannelCheckingPaymentMethodChanger:
        decorates: sylius_api.changer.payment_method
        arguments:
            - '@.inner'
            - '@sylius.repository.payment'
            - '@sylius.repository.payment_method'
            - '@sylius.resolver.payment_methods'
            - '@translator'
```

`@.inner` references the original `PaymentMethodChangerInterface` implementation, so any future Sylius change to the changer keeps working through the decorator.

#### Step 3. Clear the cache

```bash
bin/console cache:clear
```

### Reporters

We would like to extend our gratitude to the following individuals for their detailed reporting and responsible disclosure of this vulnerability:
- Fredrik Dietrichson (@FredrikEV)

### For more information

If there are any questions or comments about this advisory:

- Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues?q=sort%3Aupdated-desc+is%3Aissue+is%3Aopen)
- Send an email to [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-6955-hrm5-c4qp
- https://github.com/Sylius/Sylius
