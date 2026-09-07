# [M] Sylius Vulnerable to Authenticated Stored XSS

## Summary
Severity: Medium
Advisory: GHSA-mx4q-xxc9-pf5q
CVE: CVE-2026-31823
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-mx4q-xxc9-pf5q
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=2.0.0 <2.0.16
- Packagist: `sylius/sylius` — affected >=2.1.0 <2.1.12
- Packagist: `sylius/sylius` — affected >=2.2.0 <2.2.3

## Details
### Impact

An authenticated stored cross-site scripting (XSS) vulnerability exists in multiple places across the shop frontend and admin panel due to unsanitized entity names being rendered as raw HTML.

**Shop breadcrumbs** (`shared/breadcrumbs.html.twig`): The `breadcrumbs` macro uses the Twig `|raw` filter on label values. Since taxon names, product names, and ancestor names flow directly into these labels, a malicious taxon name like `<img src=x onerror=alert('XSS')>` is rendered and executed as JavaScript on the storefront.

**Admin product taxon picker** (`ProductTaxonTreeController.js`): The `rowRenderer` method interpolates `${name}` directly into a template literal building HTML, allowing script injection through taxon names in the admin panel.

**Admin autocomplete fields** (Tom Select): Dropdown items and options render entity names as raw HTML without escaping, allowing XSS through any autocomplete field displaying entity names.

An **authenticated administrator** can inject arbitrary HTML or JavaScript via entity names (e.g. taxon name) that is persistently rendered for all users.

### Patches

The issue is fixed in versions: 2.0.16, 2.1.12, 2.2.3 and above.

### Workarounds

Override vulnerable templates and JavaScript controllers at the project level.

---

#### Step 1 — Override shop breadcrumbs template

`templates/bundles/SyliusShopBundle/shared/breadcrumbs.html.twig`:

```twig
{% macro breadcrumbs(items) %}
    <ol class="breadcrumb" aria-label="breadcrumbs">
        {% for item in items %}
            <li class="breadcrumb-item fw-normal{{ item.active is defined and item.active ? ' active' }}">
                {% if item.path is defined %}
                    <a class="link-reset" href="{{ item.path }}" {{ item.test_attribute is defined ? sylius_test_html_attribute(item.test_attribute) }}>{{ item.label }}</a>
                {% else %}
                    <span class="text-body-tertiary text-break" {{ item.test_attribute is defined ? sylius_test_html_attribute(item.test_attribute) }}>{{ item.label }}</span>
                {% endif %}
            </li>
        {% endfor %}
    </ol>
{% endmacro %}
```

#### Step 2 — Override order breadcrumbs template

`templates/bundles/SyliusShopBundle/account/order/show/content/breadcrumbs.html.twig`:

```twig
{% from '@SyliusShop/shared/breadcrumbs.html.twig' import breadcrumbs as breadcrumbs %}

{% set order = hookable_metadata.context.order %}

<div class="col-12">
    {{ breadcrumbs([
        { label: 'sylius.ui.home'|trans, path: path('sylius_shop_homepage')},
        { label: 'sylius.ui.my_account'|trans, path: path('sylius_shop_account_dashboard')},
        { label: 'sylius.ui.order_history'|trans, path: path('sylius_shop_account_order_index')},
        { label: '#'~order.number, active: true, test_attribute: 'order-number' }
    ]) }}
</div>
```

#### Step 3 — Override ProductTaxonTreeController.js

Disable the vendor controller in `assets/admin/controllers.json`:

```diff
  "product-taxon-tree": {
-   "enabled": true,
+   "enabled": false,
    "fetch": "lazy"
  },
```

Create `assets/admin/controllers/product_taxon_tree_controller.js` — copy the original from `vendor/sylius/sylius/src/Sylius/Bundle/AdminBundle/Resources/assets/controllers/ProductTaxonTreeController.js` and apply the following change:

```diff
+ const escapeHtml = (str) => {
+     const div = document.createElement('div');
+     div.textContent = str;
+     return div.innerHTML;
+ };

  // in rowRenderer:
- <span class="infinite-tree-title">${name}</span>
+ <span class="infinite-tree-title">${escapeHtml(name)}</span>
```

Register the patched controller in `assets/admin/bootstrap.js`:

```js
import ProductTaxonTreeController from './controllers/product_taxon_tree_controller';
app.register('sylius--admin-bundle--product-taxon-tree', ProductTaxonTreeController);
```

#### Step 4 — Add autocomplete XSS protection

`assets/admin/scripts/autocomplete-xss-protection.js`:

```js
const escapeHtml = (str) => {
    if (typeof str !== 'string') return str;
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
};

document.addEventListener('autocomplete:pre-connect', (event) => {
    const options = event.detail.options;
    if (!options.render) return;

    const labelField = options.labelField || 'text';
    const wrapRenderer = (renderer) => {
        if (!renderer) return renderer;
        return (data, escape) => {
            const escaped = { ...data };
            if (escaped[labelField]) {
                escaped[labelField] = escapeHtml(escaped[labelField]);
            }
            return renderer(escaped, escape);
        };
    };

    if (options.render.item) options.render.item = wrapRenderer(options.render.item);
    if (options.render.option) options.render.option = wrapRenderer(options.render.option);
});
```

Import in `assets/admin/entrypoint.js` **before** bootstrap:

```diff
+ import './scripts/autocomplete-xss-protection';
  import './bootstrap.js';
```

#### Step 5 — Rebuild assets

```bash
yarn encore dev  # or: yarn encore production
```

### Reporters

We would like to extend our gratitude to the following individuals for their detailed reporting and responsible disclosure of this vulnerability:
- Djibril Mounkoro (@whiteov3rflow)
- Bartłomiej Nowiński (@bnBart)

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues?q=sort%3Aupdated-desc+is%3Aissue+is%3Aopen)
- Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-mx4q-xxc9-pf5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-31823
- https://github.com/Sylius/Sylius
