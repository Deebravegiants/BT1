# [C] prestashop/ps_facetedsearch: PHP Object Injection in faceted search cache allows unauthenticated RCE

## Summary
Severity: Critical
Advisory: GHSA-m5f5-28qr-9g9r
CVE: CVE-2026-54159
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-m5f5-28qr-9g9r
Type: github-advisory

## Affected
- Packagist: `prestashop/ps_facetedsearch` — affected >=3.0.0 <4.0.4

## Details
### Impact

A PHP Object Injection vulnerability affects the PrestaShop module `ps_facetedsearch`.

The module rebuilds the selected search filters from the request URL. The value of a slider filter (**price** or **weight**) is taken from the URL without sufficient validation, then stored in an internal filter-block cache where it is serialized and later read back with a raw native `unserialize()`.
By crafting that value, an attacker can smuggle a malicious serialized PHP object into the cache. When it is deserialized, a gadget chain writes an arbitrary PHP file inside the module directory, which is then used as a webshell to run commands on the server.

### Who is impacted

Any shop using a vulnerable version of `ps_facetedsearch` that displays a filter template containing a slider filter (price or weight). Exploitation is remote and **unauthenticated**, a single crafted front-office request is enough, and leads to remote code
execution and full compromise of the shop and its server.

**Affected versions:** `3.0.0` through `4.0.3` (all versions since 3.0.0, including the latest release).


### Patches

Upgrade the `ps_facetedsearch` module to the patched version. Upgrading the module is the best action that removes the vulnerability.

Otherwise, you can apply the fix manually in the file `src/Filters/Block.php`:

In the `getFromCache()` method, replace the native `unserialize()` call:

```php
// Before
if (!empty($row)) {
    return unserialize(current($row));
}

// After
if (!empty($row)) {
    return \Tools::unSerialize(current($row));
}
```

### Until the module is upgraded:

- Remove price and weight slider filters from the filter templates that are exposed on the
  front office.
- Clear the faceted-search filter cache, and audit the `modules/ps_facetedsearch/` directory for
  unexpected PHP files.
- Monitor search requests for PHP serialization patterns (`O:`, `;i:`, references to classes such
  as `Monolog\…`) and block them at the WAF level.

### Resources

- Thank you to Frédéric Moreau (Antadis) and Gilles Caudal (Datalinx) for reporting this vulnerability.

## References
- https://github.com/PrestaShop/ps_facetedsearch/security/advisories/GHSA-m5f5-28qr-9g9r
- https://github.com/PrestaShop/ps_facetedsearch
