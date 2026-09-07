# [M] Craft Commerce: Potential IDOR in Commerce carts

## Summary
Severity: Medium
Advisory: GHSA-vff3-pqq8-4cpq
CVE: CVE-2026-31867
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-vff3-pqq8-4cpq
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.6.0
- Packagist: `craftcms/commerce` — affected >=4.0.0 <4.11.0

## Details
An Insecure Direct Object Reference (IDOR) vulnerability exists in Craft Commerce’s cart functionality that allows users to hijack any shopping cart by knowing or guessing its 32-character number. This vulnerability enables the takeover of shopping sessions and potential exposure of PII.

## Vulnerability Details

### Root Cause

The `CartController` accepts a user-supplied `number` parameter to load and modify shopping carts. No ownership validation is performed - the code only checks if the order exists and is incomplete, not whether the requester has authorization to access it.

```php
// CartController.php:374-389 - actionLoadCart()
public function actionLoadCart(): ?Response
{
    $number = $this->request->getParam('number');

    if ($number === null) {
        return $this->asFailure(Craft::t('commerce', 'A cart number must be specified.'));
    }

    // No ownership check - returns any cart to any requester
    $cart = Order::find()->number($number)->isCompleted(false)->one();

    // Cart is loaded into attacker's session without authorization
    ...
}
```

```php
// CartController.php:606-616 - _getCart()
$orderNumber = $this->request->getBodyParam('number');
if ($orderNumber) {
    // Same issue - no ownership validation
    $cart = Order::find()->number($orderNumber)->isCompleted(false)->one();
    // Returns cart to any requester who knows the number
}
```
---

## Attack Scenario

### Prerequisites
- Target Craft Commerce installation with active shopping carts
- Knowledge of a victim’s cart number (32-character hex string)

### Cart Number Acquisition Vectors

1. **Referrer Header Leakage**: Cart URLs shared externally expose the number
2. **Browser History**: Accessible on shared/compromised devices
3. **Proxy/WAF Logs**: Cart numbers logged in URL parameters
4. **Social Engineering**: Support tickets, screenshots containing cart URLs
5. **Brute Force**: While impractical for random targeting, feasible for targeted attacks against recently-created carts

---

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-vff3-pqq8-4cpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-31867
- https://github.com/craftcms/commerce/pull/4207
- https://github.com/craftcms/commerce
