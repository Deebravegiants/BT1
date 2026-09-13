# [M] Sylius has a DQL Injection via API Order Filters

## Summary
Severity: Medium
Advisory: GHSA-xcwx-r2gw-w93m
CVE: CVE-2026-31825
CWE: CWE-89, CWE-943
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-xcwx-r2gw-w93m
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=0 <1.9.12
- Packagist: `sylius/sylius` — affected >=1.10.0 <1.10.16
- Packagist: `sylius/sylius` — affected >=1.11.0 <1.11.17
- Packagist: `sylius/sylius` — affected >=1.12.0 <1.12.23
- Packagist: `sylius/sylius` — affected >=1.13.0 <1.13.15
- Packagist: `sylius/sylius` — affected >=1.14.0 <1.14.18
- Packagist: `sylius/sylius` — affected >=2.0.0 <2.0.16
- Packagist: `sylius/sylius` — affected >=2.1.0 <2.1.12
- Packagist: `sylius/sylius` — affected >=2.2.0 <2.2.3

## Details
### Impact
Sylius API filters `ProductPriceOrderFilter` and `TranslationOrderNameAndLocaleFilter` pass user-supplied order direction values directly to Doctrine's `orderBy()` without validation. An attacker can inject arbitrary DQL:

```
GET /api/v2/shop/products?order[price]=ASC,%20variant.code%20DESC
```

### Patches
The issue is fixed in versions: 1.9.12, 1.10.16, 1.11.17, 1.12.23, 1.13.15, 1.14.18, 2.0.16, 2.1.12, 2.2.3 and above.

### Workarounds

An `EventSubscriber` that sanitizes `order` query parameters **only on API routes** before they reach the vulnerable filters.

The subscriber accepts an `$apiRoute` constructor parameter (default `/api/v2`) and skips non-API requests entirely — so there is zero overhead on shop/admin page requests.

This follows the same pattern used by Sylius's own `KernelRequestEventSubscriber` (`src/Sylius/Bundle/ApiBundle/EventSubscriber/KernelRequestEventSubscriber.php`), which also uses `str_contains($pathInfo, $this->apiRoute)` to scope logic to API routes.

---

#### Step 1 — Create the EventSubscriber

`src/EventSubscriber/SanitizeOrderDirectionSubscriber.php`:

```php
<?php

declare(strict_types=1);

namespace App\EventSubscriber;

use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpKernel\Event\RequestEvent;
use Symfony\Component\HttpKernel\KernelEvents;

final class SanitizeOrderDirectionSubscriber implements EventSubscriberInterface
{
    private const ALLOWED_DIRECTIONS = ['asc', 'desc'];

    public function __construct(
        private string $apiRoute,
    ) {
    }

    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::REQUEST => ['sanitizeOrderParameters', 64],
        ];
    }

    public function sanitizeOrderParameters(RequestEvent $event): void
    {
        if (!str_contains($event->getRequest()->getPathInfo(), $this->apiRoute)) {
            return;
        }

        $request = $event->getRequest();

        /** @var mixed $order */
        $order = $request->query->all()['order'] ?? null;
        if (!is_array($order)) {
            return;
        }

        $needsSanitization = false;
        $sanitized = [];
        foreach ($order as $field => $direction) {
            if (is_string($direction) && in_array(strtolower($direction), self::ALLOWED_DIRECTIONS, true)) {
                $sanitized[$field] = $direction;
            } else {
                $needsSanitization = true;
            }
        }

        if (!$needsSanitization) {
            return;
        }

        $all = $request->query->all();
        $all['order'] = $sanitized;
        $request->query->replace($all);

        $request->server->set('QUERY_STRING', http_build_query($all));
        $request->attributes->set('_api_filters', $all);
    }
}
```

#### Step 2 — Register the service

**Option A** — If your `config/services.yaml` already has `App\` autowiring (Symfony default):

```yaml
# Nothing to do — autoconfigure picks up EventSubscriberInterface automatically.
# Optionally bind the API route prefix:
services:
    App\EventSubscriber\SanitizeOrderDirectionSubscriber:
        arguments:
            $apiRoute: '%sylius.security.new_api_route%'
```

**Option B** — If there is no `App\` autowiring:

```yaml
services:
    App\EventSubscriber\SanitizeOrderDirectionSubscriber:
        arguments:
            $apiRoute: '%sylius.security.new_api_route%'
        tags: ['kernel.event_subscriber']
```

Using `%sylius.security.new_api_route%` ties the subscriber to the same prefix Sylius uses (`/api/v2` by default). If the parameter is not available, hardcode `'/api/v2'` instead.

#### Step 3 — Clear cache

```bash
bin/console cache:clear
```

### Reporters

We would like to extend our gratitude to the following individuals for their detailed reporting and responsible disclosure of this vulnerability:
- Chris Alupului (@Neosprings)
- Bartłomiej Nowiński (@bnBart)

### For more information
If you have any questions or comments about this advisory:

- Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues?q=sort%3Aupdated-desc+is%3Aissue+is%3Aopen)
- Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-xcwx-r2gw-w93m
- https://nvd.nist.gov/vuln/detail/CVE-2026-31825
- https://github.com/Sylius/Sylius
