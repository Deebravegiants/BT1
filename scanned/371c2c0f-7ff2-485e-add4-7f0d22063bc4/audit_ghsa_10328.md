# [M] OpenMage LTS: Cross-user wishlist import leads to private option & file disclosure

## Summary
Severity: Medium
Advisory: GHSA-665x-ppc4-685w
CVE: CVE-2026-40098
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-665x-ppc4-685w
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <20.17.0

## Details
# Cross-user wishlist item import via shared wishlist code, leading to private option disclosure and file-disclosure variant

## Summary

The shared wishlist add-to-cart endpoint authorizes access with a public `sharing_code`, but loads the acted-on wishlist item by a separate global `wishlist_item_id` and never verifies that the item belongs to the shared wishlist referenced by that code.

This lets an attacker use:

- a valid shared wishlist code for wishlist A
- a wishlist item ID belonging to victim wishlist B

to import victim item B into the attacker's cart through the shared wishlist flow for wishlist A.

Because the victim item's stored `buyRequest` is reused during cart import, the victim's private custom-option data is copied into the attacker's quote. If the product uses a file custom option, this can be elevated to cross-user file disclosure because the imported file metadata is preserved and the download endpoint is not ownership-bound.

## Vulnerability Type

- Broken object-level authorization / IDOR
- Cross-user data disclosure
- Cross-user file disclosure variant

## Root Cause

In `app/code/core/Mage/Wishlist/controllers/SharedController.php`, the shared flow does:

```php
$item = Mage::getModel('wishlist/item')->load($itemId);
$wishlist = Mage::getModel('wishlist/wishlist')->loadByCode($code);
...
$item->addToCart($cart);
```

Relevant lines:

- `SharedController.php:86` loads the wishlist item by global ID
- `SharedController.php:87` loads the wishlist by shared code
- `SharedController.php:99` imports the item into cart

There is no check that:

```php
$item->getWishlistId() == $wishlist->getId()
```

The safe owner flow in `app/code/core/Mage/Wishlist/controllers/IndexController.php:521-528` does preserve this binding by deriving the wishlist from `item->getWishlistId()`.

The imported item keeps its original `buyRequest` because `app/code/core/Mage/Wishlist/Model/Item.php:370-372` passes that stored request directly into:

```php
$cart->addProduct($product, $buyRequest);
```

## Security Impact

### Baseline impact

An attacker can import another user's private wishlist item into the attacker's own cart, using an unrelated shared wishlist code.

This is a clear cross-user authorization bypass. The victim item's private configuration is copied into the attacker's quote, including custom-option values such as personalized text.

### Stronger variant: cross-user file disclosure

If the victim item contains a custom option of type `file`, the imported quote item preserves file metadata such as:

- `quote_path`
- `order_path`
- `secret_key`

The file option renderer in `app/code/core/Mage/Catalog/Model/Product/Option/Type/File.php:547-552` generates a download URL from:

- the imported `sales/quote_item_option` ID
- the preserved `secret_key`

The downloader in `app/code/core/Mage/Sales/controllers/DownloadController.php:150-185`:

- loads quote item option by global ID
- verifies only product option type and `secret_key`
- reads the file from `order_path` or `quote_path`

It does not verify ownership of the quote item, order, or original wishlist item. This creates a cross-user file disclosure path once victim file metadata has been imported.

## Steps To Reproduce

### Lab data

- shared wishlist A:
  - `wishlist_id = 1`
  - `customer_id = 2`
  - `sharing_code = 6376bb8c37a09c2de3664bd8cdc16412`
- victim wishlist B:
  - `wishlist_id = 2`
  - `customer_id = 3`
- victim item:
  - `wishlist_item_id = 1`
  - `wishlist_id = 2`
  - `product_id = 2`
- victim private text option marker:
  - `VICTIM-MARKER-49040822`

### Reproduction

Send:

```http
GET /wishlist/shared/cart/?code=6376bb8c37a09c2de3664bd8cdc16412&item=1
```

Where:

- `code` belongs to shared wishlist A
- `item=1` belongs to victim wishlist B

### Expected result

The request should be rejected because the item does not belong to the shared wishlist referenced by the `sharing_code`.

### Actual result

The application imports victim item `1` into the attacker's quote anyway.

## Verified Evidence

### Baseline variant

Previously verified at quote/option level in lab:

```text
option_1 = VICTIM-MARKER-49040822
```

This shows that the attacker's cart received victim-private custom-option data from another user's wishlist item.

### File-disclosure variant

Previously verified in lab after importing a victim file-option payload:

```text
/sales/download/downloadCustomOption/id/9/key/86fca9b61c0b891b52fb/
```

This URL was generated from imported quote item option data containing the victim file metadata and secret key.

## Why This Is A Valid Bug

This is not a timing issue and does not depend on non-default security settings.

The bug is a direct authorization failure:

- authorization is based on wishlist A's share code
- the acted-on object is item B from another wishlist
- there is no item-to-wishlist binding check
- victim-controlled item state is then copied into attacker-controlled cart state

That is a broken object-level authorization issue with clear cross-user impact.

## Remediation

In `SharedController::cartAction()`, reject any request where the loaded item does not belong to the wishlist loaded from the share code:

```php
$item = Mage::getModel('wishlist/item')->load($itemId);
$wishlist = Mage::getModel('wishlist/wishlist')->loadByCode($code);

if (!$item->getId() || !$wishlist->getId() || (int) $item->getWishlistId() !== (int) $wishlist->getId()) {
    return $this->_forward('noRoute');
}
```

Defense in depth:

- bind `sales/download/downloadCustomOption` to the current quote/order owner instead of trusting only `id + secret_key`

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-665x-ppc4-685w
- https://nvd.nist.gov/vuln/detail/CVE-2026-40098
- https://github.com/OpenMage/magento-lts/pull/5446
- https://github.com/OpenMage/magento-lts
- https://github.com/OpenMage/magento-lts/releases/tag/v20.17.0
