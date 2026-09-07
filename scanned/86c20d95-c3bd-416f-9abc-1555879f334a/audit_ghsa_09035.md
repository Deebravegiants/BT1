# [M] Magento LTS Vulnerable to Open Redirect via Unvalidated `uenc` Parameter in `stockAction()`

## Summary
Severity: Medium
Advisory: GHSA-qpgq-5g92-j5q8
CVE: CVE-2026-42207
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-qpgq-5g92-j5q8
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <20.18.0

## Details
## Summary
`Mage_ProductAlert_AddController::stockAction()` reads the uenc query parameter and passes it directly to `$this->_redirectUrl($backUrl)` without calling `$this->_isUrlInternal()` When the supplied `product_id` does not match any catalog product, the server issues an unvalidated HTTP 302 redirect to whatever URL was provided as `uenc`.

## Vulnerable path:

```php
// app/code/core/Mage/ProductAlert/controllers/AddController.php : stockAction()

$backUrl = $this->getRequest()->getParam(Mage_Core_Controller_Front_Action::PARAM_NAME_URL_ENCODED);  // raw, no decode
$productId = (int) $this->getRequest()->getParam('product_id');

if (!$backUrl || !$productId) {
    $this->_redirect('/');
    return;
}

$product = Mage::getModel('catalog/product')->load($productId);

if (!$product->getId()) {
    $session->addError($this->__('Not enough parameters.'));
    $this->_redirectUrl($backUrl);   // ← NO _isUrlInternal() check
    return;
}
```

### Secure peer (priceAction()):

```php
if (!$product->getId()) {
    if ($this->_isUrlInternal($backUrl)) {  // ← validation present
        $this->_redirectUrl($backUrl);
    } else {
        $this->_redirect('/');
    }
    return;
}
```

## Steps to Reproduce

### Prerequisites
- OpenMage LTS ≤ 20.16.0 with Product Alerts enabled (default configuration)
- A valid, logged-in customer session on the target store

#### Step 1 – Authenticate as a Customer (Attacker controls the crafted link; victim must be logged in)

The `preDispatch()` hook calls `Mage::getSingleton('customer/session')->authenticate($this)`. If the request comes from an unauthenticated user, they are redirected to the login page first. The open redirect only fires after the customer is authenticated. This is the realistic attack scenario: the attacker sends a crafted link to a customer who is already logged in.

<img width="1548" height="638" alt="image" src="https://github.com/user-attachments/assets/64c18279-ec0a-4110-b8f4-d952870e348c" />

#### Step 2 – Craft the Malicious URL
The `uenc` parameter is read raw via `getParam()` with no base64 decoding in this code path. A plain URL is sufficient and produces the redirect:

```
GET /productalert/add/stock/?product_id=99999&uenc=https://evil.com/steal-credentials HTTP/1.1
Host: <store-hostname>
Cookie: om_frontend=<authenticated-session>
```

Key conditions:
- `product_id` must reference a non-existent product (triggers the vulnerable branch; any large ID works)
- `uenc` is the raw destination URL (no base64 encoding required)

<img width="1554" height="852" alt="image" src="https://github.com/user-attachments/assets/d8530247-2d2f-4747-bf16-ece71a507b50" />


## Impact

### Technical Impact
An attacker who controls the `uenc` parameter value can redirect any logged-in shopper to an arbitrary external URL. Because the redirect originates from the legitimate store domain, the victim’s browser shows the trusted store URL in the address bar momentarily before being sent to the attacker site. The HTTP 302 response exits the store’s origin before the browser shows anything to the user.

### Business-Level Attack Vectors
| Scenario                | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| Credential phishing    | Craft a link claiming to show a stock notification. Customer lands on attacker’s login clone and reuses their password. |
| OAuth / SSO token theft| If the store uses a social login or “Login with Google” flow, the attacker can inject their redirect_uri via the open redirect, stealing OAuth tokens. |
| Affiliate fraud        | Redirect customers from the legitimate store to a competing retailer after they click a “notify me” link. |
| Malware distribution   | Redirect to drive-by-download pages with the store’s reputation acting as social proof. |

### Propagation
A single malicious link can be embedded in:

- Customer emails (“Click here for stock notification preferences”)
- Forum posts, social media, or product reviews on the store
- SEO-poisoned search results that rank the store’s domain

## Recommended Fix
Apply the same `_isUrlInternal()` guard used in `priceAction()` to the `stockAction()` missing-product


This is an AI-generated report.

An attempt was made to test the same PoC against the online demo https://demo.openmage.org/ but it couldn't be reproduced. It was only reproduced against the local setup env against the latest version.

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-qpgq-5g92-j5q8
- https://nvd.nist.gov/vuln/detail/CVE-2026-42207
- https://github.com/OpenMage/magento-lts
