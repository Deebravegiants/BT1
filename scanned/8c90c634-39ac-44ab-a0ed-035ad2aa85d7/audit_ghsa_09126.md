# [M] Kimai's Twig function config() leaks server-wide secrets (LDAP bind password, SAML SP private key) via invoice/export templates

## Summary
Severity: Medium
Advisory: GHSA-vrqv-52x7-rm4v
CWE: CWE-693
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-vrqv-52x7-rm4v
Type: github-advisory

## Affected
- Packagist: `kimai/kimai` — affected >=0 <2.56.0

## Details
### Summary

Kimai's Twig sandbox (`StrictPolicy`, used for admin-uploaded invoice and export templates) allow-lists the `config()` Twig function with no key filtering. `config(name)` delegates to `App\Configuration\SystemConfiguration::find($name)`, which returns arbitrary entries from the flattened `kimai.config` container parameter built in `App\DependencyInjection\AppExtension::loadInternal()`. Any admin who can upload a Twig template can therefore render server-wide secrets - the LDAP bind password, the SAML SP private key, and any other dotted configuration key populated from `kimai.yaml` - into the invoice or export output, which is then delivered to whoever generates an invoice or export from that template (including lower-privileged users such as teamleads with invoice permissions). This is a second, uncovered class of the same defense-in-depth issue patched in GHSA-rh42-6rj2-xwmc: the previous fix added a User-method blocklist but left the `config()` function unrestricted.

### Details

`src/Twig/SecurityPolicy/StrictPolicy.php:40-55` explicitly allow-lists `'config'`:

```php
private array $allowedFunctions = [
    'max', 'min', 'range', 'constant', 'cycle', 'random', 'date',
    't',
    'encore_entry_css_source', 'encore_entry_link_tags', 'encore_entry_script_tags',
    'is_granted',
    'qr_code_data_uri',
    'config',                       // <-- sink, no key filter
    'create_date', 'month_names', 'locale_format',
    'class_name'
];
```

`src/Twig/Configuration.php:22-45` is the Twig function implementation:

```php
public function getFunctions(): array
{
    return [new TwigFunction('config', [$this, 'get'])];
}

public function get(string $name)
{
    switch ($name) {
        case 'chart-class':                     return '';
        case 'theme.chart.background_color':    return '#3c8dbc';
        // ... 4 more theme constants
    }
    return $this->configuration->find($name);   // <-- arbitrary key lookup
}
```

`App\Configuration\SystemConfiguration::find()` at `src/Configuration/SystemConfiguration.php:54-62` is a direct dictionary lookup. The dictionary `$this->settings` is initialised from the `kimai.config` container parameter, which the `AppExtension` flattens from `kimai.yaml` into dotted-notation keys.
```

The LDAP and SAML schemas declared in `src/DependencyInjection/Configuration.php` define secret-valued scalar nodes that survive the flattening and become reachable keys:

```php
// getLdapNode()
->arrayNode('connection')
    ->children()
        ->scalarNode('host')->defaultNull()->end()
        ->scalarNode('username')->end()
        ->scalarNode('password')->end()       // -> settings['ldap.connection.password']
        ...

// getSamlNode()
->arrayNode('sp')
    ->children()
        ->scalarNode('x509cert')->end()
        ->scalarNode('privateKey')->end()     // -> settings['saml.connection.sp.privateKey']
        ...
```

The invoice and export renderers both enable the sandbox against `StrictPolicy` and pass the shared Twig environment - the one with the `config` function registered - into sandboxed rendering: `src/Invoice/Renderer/AbstractTwigRenderer.php:66-74` and `src/Export/Base/{PDFRenderer,HtmlRenderer}.php`. An admin who uploads a malicious invoice or export template therefore gets an unrestricted read primitive against `kimai.config`.

In a real deployment the attacker template is uploaded through the admin UI (ROLE_SUPER_ADMIN, permission `upload_invoice_template`), saved by `src/Invoice/InvoiceTemplate*` and later rendered by whoever generates an invoice or export for that template. The rendering user is typically a teamlead or admin with invoice permission (`INVOICE` permission set: `['view_invoice','create_invoice','manage_invoice_template']`, granted to ROLE_ADMIN and ROLE_TEAMLEAD in `config/packages/kimai.yaml`). The rendered output is returned as the invoice PDF/HTML or as a CSV/XLSX export, so the secrets land in a document that is routinely downloaded and emailed.

### Impact

Any Kimai deployment that (a) has SAML or LDAP configured in `kimai.yaml`, and (b) has at least one user (other than the current SUPER_ADMIN) who will render a template-based invoice or export in the future, is affected. A malicious or compromised SUPER_ADMIN can upload a template once, leave, and subsequent invoice or export generations by teamleads or other admins silently exfiltrate `ldap.connection.password`, `saml.connection.sp.privateKey`, `saml.connection.sp.x509cert`, and any other dotted configuration key into an attacker-readable artifact. The LDAP bind password gives domain-credential access to the company directory and often to every downstream system that trusts the same directory; the SAML SP private key allows an attacker to forge signed SAML assertions to any service provider that trusts the same key pair. This is the same class of defense-in-depth leak that GHSA-rh42-6rj2-xwmc patched for user-level secrets, at a broader impact because the keys leaked here are system-wide rather than per-user, and the current StrictPolicy does not intercept the `config()` call path. 

### Solution

The `config()` function was patched to only return a pre-configured list of settings in sandboxed mode. 

Additional checks were added to prevent access to configs that start with `saml.` or `ldap.`.

Kimai will not issue a CVE, because this requires a SUPER_ADMIN account and it only affects system with activated LDAP or SAML, which also uses the invoice system.

## References
- https://github.com/kimai/kimai/security/advisories/GHSA-vrqv-52x7-rm4v
- https://github.com/kimai/kimai
