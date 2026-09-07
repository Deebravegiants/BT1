# [M] Improper Restriction of Rendered UI Layers or Frames in Sylius

## Summary
Severity: Medium
Advisory: GHSA-4jp3-q2qm-9fmw
CVE: CVE-2022-24733
CWE: CWE-1021
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-14
Source: https://github.com/advisories/GHSA-4jp3-q2qm-9fmw
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=0 <1.9.10
- Packagist: `sylius/sylius` — affected >=1.10.0 <1.10.11
- Packagist: `sylius/sylius` — affected >=1.11.0 <1.11.2

## Details
### Impact

It is possible for a page controlled by an attacker to load the website within an iframe. This will enable a clickjacking attack, in which the attacker's page overlays the target application's interface with a different interface provided by the attacker

### Patches

The issue is fixed in versions: 1.9.10, 1.10.11, 1.11.2, and above.

### Workarounds

Every response from app should have an X-Frame-Options header set to: ``sameorigin``. To achieve that you just need to add a new **subscriber** in your app. 

```php
<?php

// src/EventListener/XFrameOptionsSubscriber.php

namespace App\EventListener

final class XFrameOptionsSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::RESPONSE => 'onKernelResponse',
        ];
    }

    public function onKernelResponse(ResponseEvent $event): void
    {
        if (!$this->isMainRequest($event)) {
            return;
        }

        $response = $event->getResponse();

        $response->headers->set('X-Frame-Options', 'sameorigin');
    }

    private function isMainRequest(ResponseEvent $event): bool
    {
        if (\method_exists($event, 'isMainRequest')) {
            return $event->isMainRequest();
        }

        return $event->isMasterRequest();
    }
}

```

And register it in the container:

```yaml
# config/services.yaml
services:
    # ...
    App\EventListener\XFrameOptionsSubscriber:
        tags: ['kernel.event_subscriber']
```

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues)
* Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-4jp3-q2qm-9fmw
- https://nvd.nist.gov/vuln/detail/CVE-2022-24733
- https://github.com/Sylius/Sylius
- https://github.com/Sylius/Sylius/releases/tag/v1.10.11
- https://github.com/Sylius/Sylius/releases/tag/v1.11.2
- https://github.com/Sylius/Sylius/releases/tag/v1.9.10
