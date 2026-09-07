# [M] FacturaScripts vulnerable to stored XSS via product reference in sales/purchases

## Summary
Severity: Medium
Advisory: GHSA-r736-2678-fcrx
CVE: CVE-2026-42877
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-r736-2678-fcrx
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=0

## Details
## Summary

A stored Cross-Site Scripting (XSS) vulnerability exists in the product search modal of sales and purchases documents. An authenticated user with access to the warehouse module can create a product with a malicious reference that executes arbitrary JavaScript in the browser of any other user who opens the product search modal inside an invoice, order, or delivery note.

## Affected files

- `Core/Lib/AjaxForms/SalesModalHTML.php`
- `Core/Lib/AjaxForms/PurchasesModalHTML.php`

## Vulnerability details

The `referencia` field of a product variant is injected directly into an HTML `onclick` attribute string without JavaScript context escaping:

```php
// SalesModalHTML.php ~line 102
$tbody .= '<tr onclick="return salesFormAction(\'add-product\', \''
    . $row['referencia']   // no htmlspecialchars() applied
    . '\');">';
```

When a product is saved, `noHtml()` encodes `'` → `&#39;`. This appears safe in static HTML context. However, the modal HTML is later returned as a JSON response and inserted into the DOM via `innerHTML`:

```javascript
// SalesDocument.html.twig line 118
document.getElementById("findProductList").innerHTML = data.products;
```

The browser HTML parser decodes `&#39;` → `'` during the `innerHTML` assignment, breaking out of the JavaScript string literal in the `onclick` attribute and executing the injected code.

**Attack payload stored in database:** `x&#39;+alert(1)+&#39;`

**Resulting `onclick` after `innerHTML` decode:**
```javascript
return salesFormAction('add-product', 'x'+alert(1)+'')
//                                        ^^^^^^^^^^ executes before the function call
```

## Steps to reproduce

**Step 1 — Inject the payload**

1. Log in as a user with write access to Warehouse → Products
2. Navigate to `/EditProducto` and create a new product with the following values:

| Field | Value |
|---|---|
| Reference | `x'+alert(1)+'` |
| Description | `test` |

3. Save the product

**Step 2 — Trigger the XSS**

1. Make sure at least one customer exists in the system (Sales → Customers)
2. Navigate to `/EditFacturaCliente?codcliente=<customer_code>`
3. In the invoice form, click the product search button next to the "Referencia" field
4. Click on the 'malicious' product `alert(1)`

<img width="1162" height="536" alt="image" src="https://github.com/user-attachments/assets/aaa2879e-c1fb-4af9-8501-bac03ca24ffe" />


## Impact

Although session cookies (`fsLogkey`, `fsNick`) have the `HttpOnly` flag set and cannot be read directly via `document.cookie`, the injected script runs in the victim's authenticated browser context, meaning the attacker can make arbitrary authenticated requests on their behalf, create new admin users via AJAX POST to `/EditUser`, exfiltrate any business data visible in the DOM, or redirect the user to an external site. The most critical scenario is privilege escalation: a low-privilege employee with only warehouse
access can execute JavaScript in an administrator's session without knowing their password.

## Recommended fix

Apply `htmlspecialchars()` with `ENT_QUOTES` before inserting `referencia` into the `onclick` attribute in both affected files.

**`Core/Lib/AjaxForms/SalesModalHTML.php`**

```php
// Before (vulnerable):
$tbody .= '<tr onclick="return salesFormAction(\'add-product\', \''
    . $row['referencia']
    . '\');">';

// After (safe):
$tbody .= '<tr onclick="return salesFormAction(\'add-product\', \''
    . htmlspecialchars($row['referencia'], ENT_QUOTES, 'UTF-8')
    . '\');">';
```

**`Core/Lib/AjaxForms/PurchasesModalHTML.php`**

Apply the same change to the equivalent line.

**Why `ENT_QUOTES` is required:** `ENT_QUOTES` encodes both `"` and `'` characters. This ensures that `'` is stored as `&#39;` and — critically — remains `&#39;` after `innerHTML` assignment, because `htmlspecialchars` produces a form that the HTML parser does not decode back into a raw quote inside a JS string context.

**Alternative mitigation:** replace `innerHTML` with `innerText` or a DOM-based rendering approach that never parses injected strings as HTML. This would eliminate the entire class of HTML-injection-via-innerHTML vulnerabilities in the sales and purchases
forms.

## Credits
Omar Ramirez

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-r736-2678-fcrx
- https://nvd.nist.gov/vuln/detail/CVE-2026-42877
- https://github.com/NeoRazorX/facturascripts
