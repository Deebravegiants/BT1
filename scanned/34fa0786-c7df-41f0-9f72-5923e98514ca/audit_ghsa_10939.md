# [H] Sylius has a Promotion Usage Limit Bypass via Race Condition

## Summary
Severity: High
Advisory: GHSA-7mp4-25j8-hp5q
CVE: CVE-2026-31824
CWE: CWE-362, CWE-367
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-7mp4-25j8-hp5q
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=0 <1.9.12
- Packagist: `sylius/sylius` — affected >=1.10.0 <1.10.16
- Packagist: `sylius/sylius` — affected >=1.11.0 <1.11.17
- Packagist: `sylius/sylius` — affected >=1.12.0 <1.12.23
- Packagist: `sylius/sylius` — affected >=1.13.0 <1.13.15
- Packagist: `sylius/sylius` — affected >=1.14.0 <1.14.18
- Packagist: `sylius/sylius` — affected >=2.0.0 <2.0.16
- Packagist: `sylius/sylius` — affected >=2.1.0 <2.1.12
- Packagist: `sylius/sylius` — affected >=2.2.0 <2.2.3

## Details
### Impact
A Time-of-Check To Time-of-Use (TOCTOU) race condition was discovered in the promotion usage limit enforcement. The same class of vulnerability affects three independent limits:

1. **Promotion usage limit** - the global `used` counter on `Promotion` entities
2. **Coupon usage limit** - the global `used` counter on `PromotionCoupon` entities
3. **Coupon per-customer usage limit** - the per-customer redemption count on `PromotionCoupon` entities

In all three cases, the eligibility check reads the `used` counter (or order count) from an in-memory Doctrine entity during validation, while the actual usage increment in `OrderPromotionsUsageModifier` happens later during order completion — with no database-level locking or atomic operations between the two phases.

Because Doctrine flushes an absolute value (`SET used = 1`) rather than an atomic increment (`SET used = used + 1`), and because the affected entities lack optimistic locking, concurrent requests all read the same stale usage counts and pass the eligibility checks simultaneously.

An attacker can exploit this by preparing multiple carts with the same limited-use promotion or coupon and firing simultaneous `PATCH /api/v2/shop/orders/{token}/complete` requests. All requests pass the usage limit checks and complete successfully, allowing a single-use promotion or coupon to be redeemed an arbitrary number of times. The per-customer limit can be bypassed in the same way by a single customer completing multiple orders concurrently. No authentication is required to exploit this vulnerability.

This may lead to direct financial loss through unlimited redemption of limited-use promotions and discount coupons.

### Patches
The issue is fixed in versions: 1.9.12, 1.10.16, 1.11.17, 1.12.23, 1.13.15, 1.14.18, 2.0.16, 2.1.12, 2.2.3 and above.

### Workarounds

Decoration of the `OrderPromotionsUsageModifier` service to use atomic operations based on actual database-synchronized values.

The decorated service id in Sylius >=2.0 is `sylius.modifier.promotion.order_usage`, while <2.0 it's `sylius.promotion_usage_modifier`; The following instruction uses the latter, but it needs to be changed depending on the Sylius version.

#### Step 1. Create the decorator service

`src/Modifier/AtomicOrderPromotionsUsageModifier.php`:

```php
<?php

declare(strict_types=1);

namespace App\Modifier;

use Doctrine\DBAL\Connection;
use Doctrine\ORM\OptimisticLockException;
use Sylius\Component\Core\Model\OrderInterface;
use Sylius\Component\Core\Model\PromotionCouponInterface;
use Sylius\Component\Core\Promotion\Modifier\OrderPromotionsUsageModifierInterface;
use Sylius\Component\Promotion\Model\PromotionInterface;
// use Symfony\Component\DependencyInjection\Attribute\AsDecorator;

// #[AsDecorator(decorates: 'sylius.promotion_usage_modifier')]
final class AtomicOrderPromotionsUsageModifier implements OrderPromotionsUsageModifierInterface
{
    /** @var Connection */
    private $connection;

    public function __construct(Connection $connection)
    {
        $this->connection = $connection;
    }

    public function increment(OrderInterface $order): void
    {
        foreach ($order->getPromotions() as $promotion) {
            $this->incrementPromotionUsage($promotion);
        }

        /** @var PromotionCouponInterface|null $coupon */
        $coupon = $order->getPromotionCoupon();
        if (null === $coupon) {
            return;
        }

        $this->incrementCouponUsage($coupon, $order);
    }

    public function decrement(OrderInterface $order): void
    {
        foreach ($order->getPromotions() as $promotion) {
            $this->decrementPromotionUsage($promotion);
        }

        /** @var PromotionCouponInterface|null $coupon */
        $coupon = $order->getPromotionCoupon();
        if (null === $coupon) {
            return;
        }

        if (OrderInterface::STATE_CANCELLED === $order->getState() && !$coupon->isReusableFromCancelledOrders()) {
            return;
        }

        $this->decrementCouponUsage($coupon);
    }

    private function incrementPromotionUsage(PromotionInterface $promotion): void
    {
        $affected = $this->doExecuteStatement(
            'UPDATE sylius_promotion
             SET used = used + 1
             WHERE id = :id AND (usage_limit IS NULL OR used < usage_limit)',
            ['id' => $promotion->getId()]
        );

        if (0 === $affected) {
            throw new OptimisticLockException(sprintf('Promotion "%s" is no longer applicable.', $promotion->getCode()), $promotion);
        }

        $newUsed = (int) $this->doFetchOne(
            'SELECT used FROM sylius_promotion WHERE id = :id',
            ['id' => $promotion->getId()]
        );

        $promotion->setUsed($newUsed);
    }

    private function decrementPromotionUsage(PromotionInterface $promotion): void
    {
        $this->doExecuteStatement(
            'UPDATE sylius_promotion SET used = GREATEST(used - 1, 0) WHERE id = :id',
            ['id' => $promotion->getId()]
        );

        $newUsed = (int) $this->doFetchOne(
            'SELECT used FROM sylius_promotion WHERE id = :id',
            ['id' => $promotion->getId()]
        );

        $promotion->setUsed($newUsed);
    }

    private function incrementCouponUsage(PromotionCouponInterface $coupon, OrderInterface $order): void
    {
        $row = $this->doFetchAssociative(
            'SELECT used, usage_limit, per_customer_usage_limit FROM sylius_promotion_coupon WHERE id = :id FOR UPDATE',
            ['id' => $coupon->getId()]
        );

        if (false === $row) {
            throw new OptimisticLockException(sprintf('Promotion coupon "%s" is no longer applicable.', $coupon->getCode()), $coupon);
        }

        if (null !== $row['usage_limit'] && (int) $row['used'] >= (int) $row['usage_limit']) {
            throw new OptimisticLockException(sprintf('Promotion coupon "%s" is no longer applicable.', $coupon->getCode()), $coupon);
        }

        if (null !== $row['per_customer_usage_limit']) {
            $this->assertPerCustomerCouponUsageLimitNotReached(
                $coupon,
                $order,
                (int) $row['per_customer_usage_limit']
            );
        }

        $this->doExecuteStatement(
            'UPDATE sylius_promotion_coupon SET used = used + 1 WHERE id = :id',
            ['id' => $coupon->getId()]
        );

        $coupon->setUsed((int) $row['used'] + 1);
    }

    private function assertPerCustomerCouponUsageLimitNotReached(
        PromotionCouponInterface $coupon,
        OrderInterface $order,
        int $perCustomerUsageLimit
    ): void {
        $customer = $order->getCustomer();
        if (null === $customer || null === $customer->getId()) {
            return;
        }

        $sql = 'SELECT o.id FROM sylius_order o
                WHERE o.customer_id = :customerId
                AND o.promotion_coupon_id = :couponId
                AND o.state != :stateCart';
        $params = [
            'customerId' => $customer->getId(),
            'couponId' => $coupon->getId(),
            'stateCart' => OrderInterface::STATE_CART,
        ];

        if ($coupon->isReusableFromCancelledOrders()) {
            $sql .= ' AND o.state != :stateCancelled';
            $params['stateCancelled'] = OrderInterface::STATE_CANCELLED;
        }

        $sql .= ' FOR UPDATE';

        $count = count($this->doFetchAllAssociative($sql, $params));

        if ($count >= $perCustomerUsageLimit) {
            throw new OptimisticLockException(sprintf('Promotion coupon "%s" is no longer applicable.', $coupon->getCode()), $coupon);
        }
    }

    private function decrementCouponUsage(PromotionCouponInterface $coupon): void
    {
        $this->doExecuteStatement(
            'UPDATE sylius_promotion_coupon SET used = GREATEST(used - 1, 0) WHERE id = :id',
            ['id' => $coupon->getId()]
        );

        $newUsed = (int) $this->doFetchOne(
            'SELECT used FROM sylius_promotion_coupon WHERE id = :id',
            ['id' => $coupon->getId()]
        );

        $coupon->setUsed($newUsed);
    }

    /** @return int Number of affected rows */
    private function doExecuteStatement(string $sql, array $params): int
    {
        if (method_exists($this->connection, 'executeStatement')) {
            return $this->connection->executeStatement($sql, $params);
        }

        return $this->connection->executeUpdate($sql, $params);
    }

    /** @return mixed|false */
    private function doFetchOne(string $sql, array $params)
    {
        if (method_exists($this->connection, 'fetchOne')) {
            return $this->connection->fetchOne($sql, $params);
        }

        return $this->connection->fetchColumn($sql, $params);
    }

    /** @return array|false */
    private function doFetchAssociative(string $sql, array $params)
    {
        if (method_exists($this->connection, 'fetchAssociative')) {
            return $this->connection->fetchAssociative($sql, $params);
        }

        return $this->connection->fetchAssoc($sql, $params);
    }

    /** @return array[] */
    private function doFetchAllAssociative(string $sql, array $params): array
    {
        if (method_exists($this->connection, 'fetchAllAssociative')) {
            return $this->connection->fetchAllAssociative($sql, $params);
        }

        return $this->connection->fetchAll($sql, $params);
    }
}
```

#### Step 2. Register the service

**Option A:** If your app uses autowiring and supports the `#[AsDecorator]` attribute, uncomment it in the class and no further configuration is necessary.

**Option B:** Manually register the service in `config/services.yaml`:

```yaml
services:
    App\Modifier\AtomicOrderPromotionsUsageModifier:
        decorates: 'sylius.promotion_usage_modifier'
        arguments: ['@doctrine.dbal.default_connection']
```

#### Step 3. Update exception mapping (optional)

Check if your `api_platform` configuration maps `OptimisticLockException` to a code and update it if not:
```yaml
api_platform:
    ...
    exception_to_status:
        ...
        Doctrine\ORM\OptimisticLockException: 409
```

#### Step 4. Clear cache

```bash
bin/console cache:clear
```

### Reporters

We would like to extend our gratitude to the following individuals for their detailed reporting and responsible disclosure of this vulnerability:
- Djibril Mounkoro (@whiteov3rflow)
- Bartłomiej Nowiński (@bnBart)

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues)
- Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-7mp4-25j8-hp5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-31824
- https://github.com/Sylius/Sylius
