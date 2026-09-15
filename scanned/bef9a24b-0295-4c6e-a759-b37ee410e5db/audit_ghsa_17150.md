# [H] Shopware's session is persistent in Cache for 404 pages

## Summary
Severity: High
Advisory: GHSA-c2f9-4jmm-v45m
CVE: CVE-2024-27917
CWE: CWE-524
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-c2f9-4jmm-v45m
Type: github-advisory

## Affected
- Packagist: `shopware/storefront` — affected >=6.5.8.0 <6.5.8.7
- Packagist: `shopware/platform` — affected >=6.5.8.0 <6.5.8.7

## Details
### Impact

The Symfony Session Handler, pop's the Session Cookie and assign it to the Response. Since Shopware 6.5.8.0 the 404 pages, are cached, to improve the performance of 404 pages. So the cached Response, contains a Session Cookie when the Browser accessing the 404 page, has no cookies yet. The Symfony Session Handler is in use, when no explicit Session configuration has been done.
When Redis is in use for Sessions using the PHP Redis extension, this exploiting code is not used.

### Patches
Update to Shopware version 6.5.8.7

### Workarounds
Using Redis for Sessions, as this does not trigger the exploit code. Example configuration for Redis

```ini
# php.ini
session.save_handler = redis
session.save_path = "tcp://127.0.0.1:6379"
```

## Consequences

As an guest browser session has been cached on a 404 page, every missing image or directly reaching a 404 page will logout the customer or clear his cart.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-c2f9-4jmm-v45m
- https://github.com/shopware/shopware/commit/7d9cb03225efca5f97e69b800d8747598dd15ce3
- https://github.com/shopware/storefront/commit/3477e4a425d3c54b4bfae82d703fe3838dc21d3e
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.5.8.7
