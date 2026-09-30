# [M] Sylius PayPal Plugin has an Order Manipulation Vulnerability after PayPal Checkout

## Summary
Severity: Medium
Advisory: GHSA-hxg4-65p5-9w37
CVE: CVE-2025-30152
CWE: CWE-472
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-03-19
Source: https://github.com/advisories/GHSA-hxg4-65p5-9w37
Type: github-advisory

## Affected
- Packagist: `sylius/paypal-plugin` — affected >=0 <1.6.2
- Packagist: `sylius/paypal-plugin` — affected >=1.7.0 <1.7.2
- Packagist: `sylius/paypal-plugin` — affected >=2.0.0 <2.0.2

## Details
A discovered vulnerability allows users to modify their shopping cart after completing the PayPal Checkout process and payment authorization. If a user initiates a PayPal transaction from a product page or the cart page and then returns to the order summary page, they can still manipulate the cart contents before finalizing the order. As a result, the order amount in Sylius may be higher than the amount actually captured by PayPal, leading to a scenario where merchants deliver products or services without full payment.

### Impact

- Users can exploit this flaw to receive products/services without paying the full amount.
- Merchants may suffer financial losses due to underpaid orders.
- Trust in the integrity of the payment process is compromised.

### Patches

The issue is fixed in versions: 1.6.2, 1.7.2, 2.0.2 and above.

### Workarounds

To resolve the problem in the end application without updating to the newest patches, there is a need to overwrite `PayPalOrderCompleteProcessor` with modified logic:

```php
<?php

declare(strict_types=1);

namespace App\Processor;

use Sylius\Bundle\PayumBundle\Model\GatewayConfigInterface;
use Sylius\Component\Core\Model\OrderInterface;
use Sylius\Component\Core\Model\PaymentInterface;
use Sylius\Component\Core\Model\PaymentMethodInterface;
use Sylius\PayPalPlugin\Manager\PaymentStateManagerInterface;

final class PayPalOrderCompleteProcessor
{
    public function __construct(private readonly PaymentStateManagerInterface $paymentStateManager) {
    }

    public function completePayPalOrder(OrderInterface $order): void
    {
        $payment = $order->getLastPayment(PaymentInterface::STATE_PROCESSING);
        if ($payment === null) {
            return;
        }

        /** @var PaymentMethodInterface $paymentMethod */
        $paymentMethod = $payment->getMethod();
        /** @var GatewayConfigInterface $gatewayConfig */
        $gatewayConfig = $paymentMethod->getGatewayConfig();

        if ($gatewayConfig->getFactoryName() !== 'sylius.pay_pal') {
            return;
        }

        try {
            $this->verify($payment);
        } catch (\Exception) {
            $this->paymentStateManager->cancel($payment);

            return;
        }

        $this->paymentStateManager->complete($payment);
    }

    private function verify(PaymentInterface $payment): void
    {
        $totalAmount = $this->getTotalPaymentAmountFromPaypal($payment);

        if ($payment->getOrder()->getTotal() !== $totalAmount) {
            throw new \Exception();
        }
    }

    private function getTotalPaymentAmountFromPaypal(PaymentInterface $payment): int
    {
        $details = $payment->getDetails();

        return $details['payment_amount'] ?? 0;
    }
}
```

### IMPORTANT

For `PayPalPlugin 2.x` change:
```php
$gatewayConfig->getFactoryName() !== 'sylius.pay_pal'
```
to
```php
$gatewayConfig->getFactoryName() !== SyliusPayPalExtension::PAYPAL_FACTORY_NAME
```

Also there is a need to overwrite `CompletePayPalOrderListener` with modified logic:

```php
<?php

declare(strict_types=1);

namespace App\EventListener\Workflow;

use App\Processor\PayPalOrderCompleteProcessor;
use Sylius\Component\Core\Model\OrderInterface;
use Symfony\Component\Workflow\Event\CompletedEvent;
use Webmozart\Assert\Assert;

final class CompletePayPalOrderListener
{
    public function __construct(private readonly PayPalOrderCompleteProcessor $completeProcessor)
    {
    }

    public function __invoke(CompletedEvent $event): void
    {
        /** @var OrderInterface $order */
        $order = $event->getSubject();
        Assert::isInstanceOf($order, OrderInterface::class);

        $this->completeProcessor->completePayPalOrder($order);
    }
}

```

And to overwrite `CaptureAction` with modified logic (if you didn't have it already):

```php
<?php

declare(strict_types=1);

namespace App\Payum\Action;

use Payum\Core\Action\ActionInterface;
use Payum\Core\Exception\RequestNotSupportedException;
use Payum\Core\Request\Capture;
use Sylius\Component\Core\Model\PaymentInterface;
use Sylius\Component\Core\Model\PaymentMethodInterface;
use Sylius\PayPalPlugin\Api\CacheAuthorizeClientApiInterface;
use Sylius\PayPalPlugin\Api\CreateOrderApiInterface;
use Sylius\PayPalPlugin\Payum\Action\StatusAction;
use Sylius\PayPalPlugin\Provider\UuidProviderInterface;

final class CaptureAction implements ActionInterface
{
    public function __construct(
        private CacheAuthorizeClientApiInterface $authorizeClientApi,
        private CreateOrderApiInterface $createOrderApi,
        private UuidProviderInterface $uuidProvider,
    ) {
    }

    /** @param Capture $request */
    public function execute($request): void
    {
        RequestNotSupportedException::assertSupports($this, $request);

        /** @var PaymentInterface $payment */
        $payment = $request->getModel();
        /** @var PaymentMethodInterface $paymentMethod */
        $paymentMethod = $payment->getMethod();

        $token = $this->authorizeClientApi->authorize($paymentMethod);

        $referenceId = $this->uuidProvider->provide();
        $content = $this->createOrderApi->create($token, $payment, $referenceId);

        if ($content['status'] === 'CREATED') {
            $payment->setDetails([
                'status' => StatusAction::STATUS_CAPTURED,
                'paypal_order_id' => $content['id'],
                'reference_id' => $referenceId,
                'payment_amount' => $payment->getAmount(),
            ]);
        }
    }

    public function supports($request): bool
    {
        return
            $request instanceof Capture &&
            $request->getModel() instanceof PaymentInterface
        ;
    }
}
```

After that, register services in the container when using PayPal 1.x:

```yaml
Sylius\PayPalPlugin\EventListener\Workflow\CompletePayPalOrderListener:
    class: App\EventListener\Workflow\CompletePayPalOrderListener
    public: true
    arguments:
        - '@Sylius\PayPalPlugin\Processor\PayPalOrderCompleteProcessor'
    tags: 
        - { name: 'kernel.event_listener', event: 'workflow.sylius_order_checkout.completed.complete', priority: 100 }
    
Sylius\PayPalPlugin\Processor\PayPalOrderCompleteProcessor:
    class: App\Processor\PayPalOrderCompleteProcessor
    public: true
    arguments:
        - '@Sylius\PayPalPlugin\Manager\PaymentStateManagerInterface'

Sylius\PayPalPlugin\Payum\Action\CaptureAction:
    class: App\Payum\Action\CaptureAction
    public: true
    arguments:
        - '@Sylius\PayPalPlugin\Api\CacheAuthorizeClientApiInterface'
        - '@Sylius\PayPalPlugin\Api\CreateOrderApiInterface'
        - '@Sylius\PayPalPlugin\Provider\UuidProviderInterface'
    tags:
        - { name: 'payum.action', factory: 'sylius.pay_pal', alias: 'payum.action.capture' }
```

or when using PayPal 2.x:

```yaml
sylius_paypal.listener.workflow.complete_paypal_order:
    class: App\EventListener\Workflow\CompletePayPalOrderListener
    public: true
    arguments:
        - '@sylius_paypal.processor.paypal_order_complete'
    tags: 
        - { name: 'kernel.event_listener', event: 'workflow.sylius_order_checkout.completed.complete', priority: 100 }
    
sylius_paypal.processor.paypal_order_complete:
    class: App\Processor\PayPalOrderCompleteProcessor
    public: true
    arguments:
        - '@sylius_paypal.manager.payment_state'

sylius_paypal.payum.action.capture:
    class: App\Payum\Action\CaptureAction
    public: true
    arguments:
        - '@sylius_paypal.api.cache_authorize_client'
        - '@sylius_paypal.api.create_order'
        - '@sylius_paypal.provider.uuid'
    tags:
        - { name: 'payum.action', factory: 'sylius.paypal', alias: 'payum.action.capture' }
```

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues)
* Email us at security@sylius.com

## References
- https://github.com/Sylius/PayPalPlugin/security/advisories/GHSA-hxg4-65p5-9w37
- https://nvd.nist.gov/vuln/detail/CVE-2025-30152
- https://github.com/Sylius/PayPalPlugin/commit/5613df827a6d4fc50862229295976200a68e97aa
- https://github.com/Sylius/PayPalPlugin
