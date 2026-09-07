# [M] Craft Commerce has Stored DOM XSS in Order Status Name (Reflects in "Recent Orders" Dashboard Widget)

## Summary
Severity: Medium
Advisory: GHSA-frj9-9rwc-pw9j
CVE: CVE-2026-25482
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-frj9-9rwc-pw9j
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.5.2
- Packagist: `craftcms/commerce` — affected >=4.0.0-RC1 <4.10.1

## Details
## Summary

A stored DOM XSS vulnerability exists in the **"Recent Orders"** dashboard widget. The Order Status Name is rendered via JavaScript string concatenation without proper escaping, allowing script execution when any admin visits the dashboard.

Users are recommended to update to the patched 5.5.2 release to mitigate the issue.

---
## Proof of Concept

### Required Permissions

- Admin access (to edit/create Order Statuses)

### Steps to Reproduce
1. Log in with an admin account
2. Navigate to **Commerce** → **Settings** → **Order Statuses**
3. Create new order status (e.g., "Pending")
4. Set the **Name** field to:
```html
<img src=x onerror="alert('Order Statuses XSS')" hidden>
```
5. Save the order status
6. Go to Commerce Orders & make some orders with different statuses (e.g. "New" & "the malicious created status")
7. Go to the Dashboard (`/admin/dashboard`) & Add **"Recent Orders"** widget and pick the same 2 statuses for orders
8. Notice the XSS execution <img width="1491" height="568" alt="xss-execution-in-dashboard" src="https://github.com/user-attachments/assets/84e8b121-30b9-4029-93be-e90009b6897e" />


---
## Technical Details

**File:** `vendor/craftcms/commerce/src/templates/_components/widgets/orders/recent/body.twig`

**Root Cause:** `value.name` (the Order Status Name) is concatenated directly into the HTML string without sanitization. When JavaScript inserts this HTML into the DOM, any malicious tags/scripts in the name are executed.<img width="1780" height="858" alt="vulnerable-code" src="https://github.com/user-attachments/assets/b150ee9d-c072-4987-b506-81a29c23d84b" />

---
## Mitigation
Use `Craft.escapeHtml()` in the callback:
```javascript
callback: function(value) {
    return '<span class="commerceStatusLabel"><span class="status ' + Craft.escapeHtml(value.color) + '"></span>' + Craft.escapeHtml(value.name) + '</span>';
}
```

## Resources:

https://github.com/craftcms/commerce/commit/d94d1c9832a47a1c383e375ae87c46c13935ba65

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-frj9-9rwc-pw9j
- https://nvd.nist.gov/vuln/detail/CVE-2026-25482
- https://github.com/craftcms/commerce/commit/d94d1c9832a47a1c383e375ae87c46c13935ba65
- https://github.com/craftcms/commerce
- https://github.com/craftcms/commerce/releases/tag/4.10.1
- https://github.com/craftcms/commerce/releases/tag/5.5.2
