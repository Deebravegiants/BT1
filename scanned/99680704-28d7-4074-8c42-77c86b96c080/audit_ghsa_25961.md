# [M] Sensitive Information Exposure in Sylius

## Summary
Severity: Medium
Advisory: GHSA-7563-75j9-6h5p
CVE: CVE-2022-24742
CWE: CWE-200, CWE-213, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-14
Source: https://github.com/advisories/GHSA-7563-75j9-6h5p
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=0 <1.9.10
- Packagist: `sylius/sylius` — affected >=1.10 <1.10.11
- Packagist: `sylius/sylius` — affected >=1.11 <1.11.2

## Details
### Impact
Any other user can view the data if the browser tab remains open after logging out. Once someone logs out and leaves the browser open, the potential attacker may use the back button to see the content exposed on given screens. No action may be performed though, and any website refresh will block further reads. It may, however, lead to a data leak, like for example customer details, payment gateway configuration, etc.- but only if these were pages checked by the administrator. 

This vulnerability requires full access to the computer to take advantage of it.

### Patches
The issue is fixed in versions: 1.9.10, 1.10.11, 1.11.2 and above.

### Workarounds
The application must strictly redirect to the login page even when the browser back button is pressed. Another possibility is to set more strict cache policies for restricted content (like no-store). It can be achieved with the following class:

```php
<?php

declare(strict_types=1);

namespace App\EventListener;

use App\SectionResolver\ShopCustomerAccountSubSection;
use Sylius\Bundle\AdminBundle\SectionResolver\AdminSection;
use Sylius\Bundle\CoreBundle\SectionResolver\SectionProviderInterface;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpKernel\Event\ResponseEvent;
use Symfony\Component\HttpKernel\KernelEvents;

final class CacheControlSubscriber implements EventSubscriberInterface
{
    /** @var SectionProviderInterface */
    private $sectionProvider;

    public function __construct(SectionProviderInterface $sectionProvider)
    {
        $this->sectionProvider = $sectionProvider;
    }

    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::RESPONSE => 'setCacheControlDirectives',
        ];
    }

    public function setCacheControlDirectives(ResponseEvent $event): void
    {
        if (
            !$this->sectionProvider->getSection() instanceof AdminSection &&
            !$this->sectionProvider->getSection() instanceof ShopCustomerAccountSubSection
        ) {
            return;
        }

        $response = $event->getResponse();

        $response->headers->addCacheControlDirective('no-cache', true);
        $response->headers->addCacheControlDirective('max-age', '0');
        $response->headers->addCacheControlDirective('must-revalidate', true);
        $response->headers->addCacheControlDirective('no-store', true);
    }
}
```

After that register service in the container:

```yaml
services:
    App\EventListener\CacheControlSubscriber:
        arguments: ['@sylius.section_resolver.uri_based_section_resolver']
        tags:
            - { name: kernel.event_subscriber, event: kernel.response }
```

The code above requires changes in `ShopUriBasedSectionResolver` in order to work. To backport mentioned logic, you need to replace the `Sylius\Bundle\ShopBundle\SectionResolver\ShopUriBasedSectionResolver` class with:

```php
<?php

declare(strict_types=1);

namespace App\SectionResolver;

use Sylius\Bundle\CoreBundle\SectionResolver\SectionInterface;
use Sylius\Bundle\CoreBundle\SectionResolver\UriBasedSectionResolverInterface;
use Sylius\Bundle\ShopBundle\SectionResolver\ShopSection;

final class ShopUriBasedSectionResolver implements UriBasedSectionResolverInterface
{
    /** @var string */
    private $shopCustomerAccountUri;

    public function __construct(string $shopCustomerAccountUri = 'account')
    {
        $this->shopCustomerAccountUri = $shopCustomerAccountUri;
    }

    public function getSection(string $uri): SectionInterface
    {
        if (str_contains($uri, $this->shopCustomerAccountUri)) {
            return new ShopCustomerAccountSubSection();
        }

        return new ShopSection();
    }
}
```

```yaml
services:
    sylius.section_resolver.shop_uri_based_section_resolver:
        class: App\SectionResolver\ShopUriBasedSectionResolver
        tags:
            - { name: sylius.uri_based_section_resolver, priority: -10 }
```

You also need to define a new subsection for the Customer Account that is used in the above services:

```php
<?php

declare(strict_types=1);

namespace App\SectionResolver;

use Sylius\Bundle\ShopBundle\SectionResolver\ShopSection;

class ShopCustomerAccountSubSection extends ShopSection
{
}
```

### References
* Originally published at https://huntr.dev/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues)
* Email us at security@sylius.com

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-7563-75j9-6h5p
- https://nvd.nist.gov/vuln/detail/CVE-2022-24742
- https://github.com/Sylius/Sylius
- https://github.com/Sylius/Sylius/releases/tag/v1.10.11
- https://github.com/Sylius/Sylius/releases/tag/v1.11.2
- https://github.com/Sylius/Sylius/releases/tag/v1.9.10
