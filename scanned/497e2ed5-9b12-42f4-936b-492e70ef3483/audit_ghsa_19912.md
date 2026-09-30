# [M] Sylius PayPal Plugin Payment Amount Manipulation Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-pqq3-q84h-pj6x
CVE: CVE-2025-29788
CWE: CWE-472
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-03-17
Source: https://github.com/advisories/GHSA-pqq3-q84h-pj6x
Type: github-advisory

## Affected
- Packagist: `sylius/paypal-plugin` — affected >=0 <1.6.1
- Packagist: `sylius/paypal-plugin` — affected >=1.7.0 <1.7.1
- Packagist: `sylius/paypal-plugin` — affected >=2.0.0 <2.0.1

## Details
A vulnerability allows users to manipulate the final payment amount processed by PayPal. If a user modifies the item quantity in their shopping cart after initiating the PayPal Checkout process, PayPal will not receive the updated total amount. As a result, PayPal captures only the initially transmitted amount, while Sylius incorrectly considers the order fully paid based on the modified total. This flaw can be exploited both accidentally and intentionally, potentially enabling fraud by allowing customers to pay less than the actual order value.

### Impact

- Attackers can intentionally pay less than the actual total order amount.
- Business owners may suffer financial losses due to underpaid orders.
- Integrity of payment processing is compromised.

### Patches

The issue is fixed in versions: 1.6.1, 1.7.1, 2.0.1 and above.

### Workarounds

To resolve the problem in the end application without updating to the newest patches, there is a need to overwrite `ProcessPayPalOrderAction` with modified logic:

```php
<?php

declare(strict_types=1);

namespace App\Controller;

use Doctrine\Persistence\ObjectManager;
use SM\Factory\FactoryInterface as StateMachineFactoryInterface;
use Sylius\Abstraction\StateMachine\StateMachineInterface;
use Sylius\Abstraction\StateMachine\WinzouStateMachineAdapter;
use Sylius\Component\Core\Factory\AddressFactoryInterface;
use Sylius\Component\Core\Model\CustomerInterface;
use Sylius\Component\Core\Model\PaymentInterface;
use Sylius\Component\Core\Model\PaymentMethodInterface;
use Sylius\Component\Core\OrderCheckoutTransitions;
use Sylius\Component\Core\Repository\CustomerRepositoryInterface;
use Sylius\Component\Resource\Factory\FactoryInterface;
use Sylius\PayPalPlugin\Api\CacheAuthorizeClientApiInterface;
use Sylius\PayPalPlugin\Api\OrderDetailsApiInterface;
use Sylius\PayPalPlugin\Manager\PaymentStateManagerInterface;
use Sylius\PayPalPlugin\Provider\OrderProviderInterface;
use Sylius\PayPalPlugin\Verifier\PaymentAmountVerifierInterface;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

final class ProcessPayPalOrderAction
{
    public function __construct(
        private readonly CustomerRepositoryInterface $customerRepository,
        private readonly FactoryInterface $customerFactory,
        private readonly AddressFactoryInterface $addressFactory,
        private readonly ObjectManager $orderManager,
        private readonly StateMachineFactoryInterface|StateMachineInterface $stateMachineFactory,
        private readonly PaymentStateManagerInterface $paymentStateManager,
        private readonly CacheAuthorizeClientApiInterface $authorizeClientApi,
        private readonly OrderDetailsApiInterface $orderDetailsApi,
        private readonly OrderProviderInterface $orderProvider,
    ) {
    }

    public function __invoke(Request $request): Response
    {
        $orderId = $request->request->getInt('orderId');
        $order = $this->orderProvider->provideOrderById($orderId);
        /** @var PaymentInterface $payment */
        $payment = $order->getLastPayment(PaymentInterface::STATE_CART);

        $data = $this->getOrderDetails((string) $request->request->get('payPalOrderId'), $payment);

        /** @var CustomerInterface|null $customer */
        $customer = $order->getCustomer();
        if ($customer === null) {
            $customer = $this->getOrderCustomer($data['payer']);
            $order->setCustomer($customer);
        }

        $purchaseUnit = (array) $data['purchase_units'][0];

        $address = $this->addressFactory->createNew();

        if ($order->isShippingRequired()) {
            $name = explode(' ', $purchaseUnit['shipping']['name']['full_name']);
            $address->setLastName(array_pop($name) ?? '');
            $address->setFirstName(implode(' ', $name));
            $address->setStreet($purchaseUnit['shipping']['address']['address_line_1']);
            $address->setCity($purchaseUnit['shipping']['address']['admin_area_2']);
            $address->setPostcode($purchaseUnit['shipping']['address']['postal_code']);
            $address->setCountryCode($purchaseUnit['shipping']['address']['country_code']);

            $this->getStateMachine()->apply($order, OrderCheckoutTransitions::GRAPH, OrderCheckoutTransitions::TRANSITION_ADDRESS);
            $this->getStateMachine()->apply($order, OrderCheckoutTransitions::GRAPH, OrderCheckoutTransitions::TRANSITION_SELECT_SHIPPING);
        } else {
            $address->setFirstName($customer->getFirstName());
            $address->setLastName($customer->getLastName());

            $defaultAddress = $customer->getDefaultAddress();

            $address->setStreet($defaultAddress ? $defaultAddress->getStreet() : '');
            $address->setCity($defaultAddress ? $defaultAddress->getCity() : '');
            $address->setPostcode($defaultAddress ? $defaultAddress->getPostcode() : '');
            $address->setCountryCode($data['payer']['address']['country_code']);

            $this->getStateMachine()->apply($order, OrderCheckoutTransitions::GRAPH, OrderCheckoutTransitions::TRANSITION_ADDRESS);
        }

        $order->setShippingAddress(clone $address);
        $order->setBillingAddress(clone $address);

        $this->getStateMachine()->apply($order, OrderCheckoutTransitions::GRAPH, OrderCheckoutTransitions::TRANSITION_SELECT_PAYMENT);

        $this->orderManager->flush();

        try {
            $this->verify($payment, $data);
        } catch (\Exception) {
            $this->paymentStateManager->cancel($payment);

            return new JsonResponse(['orderID' => $order->getId()]);
        }

        $this->paymentStateManager->create($payment);
        $this->paymentStateManager->process($payment);

        return new JsonResponse(['orderID' => $order->getId()]);
    }

    private function getOrderCustomer(array $customerData): CustomerInterface
    {
        /** @var CustomerInterface|null $existingCustomer */
        $existingCustomer = $this->customerRepository->findOneBy(['email' => $customerData['email_address']]);
        if ($existingCustomer !== null) {
            return $existingCustomer;
        }

        /** @var CustomerInterface $customer */
        $customer = $this->customerFactory->createNew();
        $customer->setEmail($customerData['email_address']);
        $customer->setFirstName($customerData['name']['given_name']);
        $customer->setLastName($customerData['name']['surname']);

        return $customer;
    }

    private function getOrderDetails(string $id, PaymentInterface $payment): array
    {
        /** @var PaymentMethodInterface $paymentMethod */
        $paymentMethod = $payment->getMethod();
        $token = $this->authorizeClientApi->authorize($paymentMethod);

        return $this->orderDetailsApi->get($token, $id);
    }

    private function getStateMachine(): StateMachineInterface
    {
        if ($this->stateMachineFactory instanceof StateMachineFactoryInterface) {
            return new WinzouStateMachineAdapter($this->stateMachineFactory);
        }

        return $this->stateMachineFactory;
    }

    private function verify(PaymentInterface $payment, array $paypalOrderDetails): void
    {
        $totalAmount = $this->getTotalPaymentAmountFromPaypal($paypalOrderDetails);

        if ($payment->getAmount() !== $totalAmount) {
            throw new \Exception();
        }
    }

    private function getTotalPaymentAmountFromPaypal(array $paypalOrderDetails): int
    {
        if (!isset($paypalOrderDetails['purchase_units']) || !is_array($paypalOrderDetails['purchase_units'])) {
            return 0;
        }

        $totalAmount = 0;

        foreach ($paypalOrderDetails['purchase_units'] as $unit) {
            $stringAmount = $unit['amount']['value'] ?? '0';

            $totalAmount += (int) ($stringAmount * 100);
        }

        return $totalAmount;
    }
}
```

Also there is a need to overwrite `CompletePayPalOrderFromPaymentPageAction` with modified logic:

```php
<?php

declare(strict_types=1);

namespace App\Controller;

use Doctrine\Persistence\ObjectManager;
use SM\Factory\FactoryInterface;
use Sylius\Abstraction\StateMachine\StateMachineInterface;
use Sylius\Abstraction\StateMachine\WinzouStateMachineAdapter;
use Sylius\Component\Core\Model\PaymentInterface;
use Sylius\Component\Core\OrderCheckoutTransitions;
use Sylius\Component\Order\Processor\OrderProcessorInterface;
use Sylius\PayPalPlugin\Exception\PaymentAmountMismatchException;
use Sylius\PayPalPlugin\Manager\PaymentStateManagerInterface;
use Sylius\PayPalPlugin\Provider\OrderProviderInterface;
use Sylius\PayPalPlugin\Verifier\PaymentAmountVerifierInterface;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Generator\UrlGeneratorInterface;

final class CompletePayPalOrderFromPaymentPageAction
{
    public function __construct(
        private readonly PaymentStateManagerInterface $paymentStateManager,
        private readonly UrlGeneratorInterface $router,
        private readonly OrderProviderInterface $orderProvider,
        private readonly FactoryInterface|StateMachineInterface $stateMachine,
        private readonly ObjectManager $orderManager,
        private readonly OrderProcessorInterface $orderProcessor,
    ) {
    }

    public function __invoke(Request $request): Response
    {
        $orderId = $request->attributes->getInt('id');

        $order = $this->orderProvider->provideOrderById($orderId);
        /** @var PaymentInterface $payment */
        $payment = $order->getLastPayment(PaymentInterface::STATE_PROCESSING);

        try {
            $this->verify($payment);
        } catch (\Exception) {
            $this->paymentStateManager->cancel($payment);
            $order->removePayment($payment);

            $this->orderProcessor->process($order);

            return new JsonResponse([
                'return_url' => $this->router->generate('sylius_shop_checkout_complete', [], UrlGeneratorInterface::ABSOLUTE_URL),
            ]);
        }

        $this->paymentStateManager->complete($payment);

        $this->getStateMachine()->apply($order, OrderCheckoutTransitions::GRAPH, OrderCheckoutTransitions::TRANSITION_SELECT_PAYMENT);
        $this->getStateMachine()->apply($order, OrderCheckoutTransitions::GRAPH, OrderCheckoutTransitions::TRANSITION_COMPLETE);

        $this->orderManager->flush();

        $request->getSession()->set('sylius_order_id', $order->getId());

        return new JsonResponse([
            'return_url' => $this->router->generate('sylius_shop_order_thank_you', [], UrlGeneratorInterface::ABSOLUTE_URL),
        ]);
    }

    private function getStateMachine(): StateMachineInterface
    {
        if ($this->stateMachine instanceof FactoryInterface) {
            return new WinzouStateMachineAdapter($this->stateMachine);
        }

        return $this->stateMachine;
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

And to overwrite `CaptureAction` with modified logic:

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
services:
    App\Controller\ProcessPayPalOrderAction:
        class: App\Controller\ProcessPayPalOrderAction
        public: true
        arguments:
            - '@sylius.repository.customer'
            - '@sylius.factory.customer'
            - '@sylius.factory.address'
            - '@sylius.manager.order'
            - '@sylius_abstraction.state_machine'
            - '@Sylius\PayPalPlugin\Manager\PaymentStateManagerInterface'
            - '@Sylius\PayPalPlugin\Api\CacheAuthorizeClientApiInterface'
            - '@Sylius\PayPalPlugin\Api\OrderDetailsApiInterface'
            - '@Sylius\PayPalPlugin\Provider\OrderProviderInterface'

    Sylius\PayPalPlugin\Controller\ProcessPayPalOrderAction:
        alias: App\Controller\ProcessPayPalOrderAction

    App\Controller\CompletePayPalOrderFromPaymentPageAction:
        class: App\Controller\CompletePayPalOrderFromPaymentPageAction
        public: true
        arguments:
            - '@Sylius\PayPalPlugin\Manager\PaymentStateManagerInterface'
            - '@router'
            - '@Sylius\PayPalPlugin\Provider\OrderProviderInterface'
            - '@sylius_abstraction.state_machine'
            - '@sylius.manager.order'
            - '@sylius.order_processing.order_processor'

    Sylius\PayPalPlugin\Controller\CompletePayPalOrderFromPaymentPageAction:
        alias: App\Controller\CompletePayPalOrderFromPaymentPageAction

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
services:
    App\Controller\ProcessPayPalOrderAction:
        class: App\Controller\ProcessPayPalOrderAction
        public: true
        arguments:
            - '@sylius.repository.customer'
            - '@sylius.factory.customer'
            - '@sylius.factory.address'
            - '@sylius.manager.order'
            - '@sylius_abstraction.state_machine'
            - '@sylius_paypal.manager.payment_state'
            - '@sylius_paypal.api.cache_authorize_client'
            - '@sylius_paypal.api.order_details'
            - '@sylius_paypal.provider.order'

    sylius_paypal.controller.process_paypal_order:
        alias: App\Controller\ProcessPayPalOrderAction

    App\Controller\CompletePayPalOrderFromPaymentPageAction:
        class: App\Controller\CompletePayPalOrderFromPaymentPageAction
        public: true
        arguments:
            - '@sylius_paypal.manager.payment_state'
            - '@router'
            - '@sylius_paypal.provider.order'
            - '@sylius_abstraction.state_machine'
            - '@sylius.manager.order'
            - '@sylius.order_processing.order_processor'

    sylius_paypal.controller.complete_paypal_order_from_payment_page:
        alias: App\Controller\CompletePayPalOrderFromPaymentPageAction

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
- https://github.com/Sylius/PayPalPlugin/security/advisories/GHSA-pqq3-q84h-pj6x
- https://nvd.nist.gov/vuln/detail/CVE-2025-29788
- https://github.com/Sylius/PayPalPlugin/commit/31e71b0457e5d887a6c19f8cfabb8b16125ec406
- https://github.com/Sylius/PayPalPlugin/commit/8a81258f965b7860d4bccb52942e4c5b53e6774d
- https://github.com/Sylius/PayPalPlugin
- https://github.com/Sylius/PayPalPlugin/releases/tag/v1.6.1
- https://github.com/Sylius/PayPalPlugin/releases/tag/v1.7.1
- https://github.com/Sylius/PayPalPlugin/releases/tag/v2.0.1
