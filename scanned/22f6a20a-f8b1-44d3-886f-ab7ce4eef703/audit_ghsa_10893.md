# [M] Sylius has an Open Redirect via Referer Header

## Summary
Severity: Medium
Advisory: GHSA-9ffx-f77r-756w
CVE: CVE-2026-31819
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-9ffx-f77r-756w
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
`CurrencySwitchController::switchAction()`, `ImpersonateUserController::impersonateAction()` and `StorageBasedLocaleSwitcher::handle()` use the HTTP Referer header directly when redirecting.

The attack requires the victim to click a legitimate application link placed on an attacker-controlled page. The browser automatically sends the attacker's site as the Referer, and the application redirects back to it. This can be used for phishing or credential theft, as the redirect originates from a trusted domain.

The severity varies by endpoint; public endpoints require no authentication and are trivially exploitable, while admin-only endpoints require an authenticated session but remain vulnerable if an admin follows a link from an external source such as email or chat.

Affected classes:
- `CurrencySwitchController::switchAction()` - public
- `StorageBasedLocaleSwitcher::handle()` - public, used in locale switching without having locale in the `url`
- `ImpersonateUserController::impersonateAction()` - admin-only

### Patches
The issue is fixed in versions: 1.9.12, 1.10.16, 1.11.17, 1.12.23, 1.13.15, 1.14.18, 2.0.16, 2.1.12, 2.2.3 and above.

### Workarounds
If you cannot update Sylius immediately, copy the affected classes from vendor to your project's `src/` directory, apply the fix, and override the service definitions.

#### Step 1 - CurrencySwitchController

Copy from `vendor/sylius/sylius/src/Sylius/Bundle/ShopBundle/Controller/CurrencySwitchController.php` to `src/Controller/CurrencySwitchController.php` and apply the following changes:

```diff
-namespace Sylius\Bundle\ShopBundle\Controller;
+namespace App\Controller;

 use Sylius\Component\Channel\Context\ChannelContextInterface;
 use Sylius\Component\Core\Currency\CurrencyStorageInterface;
 use Sylius\Component\Core\Model\ChannelInterface;
 use Symfony\Component\HttpFoundation\RedirectResponse;
 use Symfony\Component\HttpFoundation\Request;
 use Symfony\Component\HttpFoundation\Response;
+use Symfony\Component\Routing\RouterInterface;

 final class CurrencySwitchController
 {
     public function __construct(
         private Environment $templatingEngine, // for 1.x version
         private CurrencyStorageInterface $currencyStorage,
         private ChannelContextInterface $channelContext,
+        private RouterInterface $router,
     ) {
     }

     public function switchAction(Request $request, string $code): Response
     {
         /** @var ChannelInterface $channel */
         $channel = $this->channelContext->getChannel();

         $this->currencyStorage->set($channel, $code);

-        return new RedirectResponse($request->headers->get('referer', $request->getSchemeAndHttpHost()));
+        return new RedirectResponse($this->router->generate('sylius_shop_homepage'));
     }
 }
```

#### Step 2 - ImpersonateUserController

Copy from `vendor/sylius/sylius/src/Sylius/Bundle/AdminBundle/Controller/ImpersonateUserController.php` to `src/Controller/Admin/ImpersonateUserController.php` and apply the following changes:

```diff
-namespace Sylius\Bundle\AdminBundle\Controller;
+namespace App\Controller\Admin;

 // ... (keep all existing use statements)

     public function impersonateAction(Request $request, string $username): Response
     {
         // ... (keep authorization check and impersonation logic)

         $this->addFlash($request, $username);

-        $redirectUrl = $request->headers->get(
-            'referer',
+        return new RedirectResponse(
             $this->router->generate('sylius_admin_customer_show', ['id' => $user->getId()])
         );
-
-        return new RedirectResponse($redirectUrl);
     }
```

#### Step 3 - StorageBasedLocaleSwitcher (only if you use `locale_switcher: storage`)

> **Note:** Skip this step if you use the default `locale_switcher: url` mode.

Copy from `vendor/sylius/sylius/src/Sylius/Bundle/ShopBundle/Locale/StorageBasedLocaleSwitcher.php` to `src/Locale/StorageBasedLocaleSwitcher.php` and apply the following changes:

**For Sylius 1.9 – 2.1.2:**

```diff
-namespace Sylius\Bundle\ShopBundle\Locale;
+namespace App\Locale;

 use Sylius\Bundle\ShopBundle\Locale\LocaleSwitcherInterface;
 use Sylius\Component\Channel\Context\ChannelContextInterface;
 use Sylius\Component\Core\Locale\LocaleStorageInterface;
 use Symfony\Component\HttpFoundation\RedirectResponse;
 use Symfony\Component\HttpFoundation\Request;
+use Symfony\Component\Routing\RouterInterface;

 final class StorageBasedLocaleSwitcher implements LocaleSwitcherInterface
 {
     public function __construct(
         private LocaleStorageInterface $localeStorage,
         private ChannelContextInterface $channelContext,
+        private RouterInterface $router,
     ) {
     }

     public function handle(Request $request, string $localeCode): RedirectResponse
     {
         $this->localeStorage->set($this->channelContext->getChannel(), $localeCode);

-        return new RedirectResponse($request->headers->get('referer', $request->getSchemeAndHttpHost()));
+        return new RedirectResponse($this->router->generate('sylius_shop_homepage'));
     }
 }
```

**For Sylius 2.1.3 and later:**

> In Sylius 2.1.3 the class was refactored to use `UrlMatcherInterface`. While this adds partial validation, it still passes the full referer URL to `RedirectResponse`, so the open redirect remains exploitable.

```diff
-namespace Sylius\Bundle\ShopBundle\Locale;
+namespace App\Locale;

 use Sylius\Bundle\ShopBundle\Locale\LocaleSwitcherInterface;
 use Sylius\Component\Channel\Context\ChannelContextInterface;
 use Sylius\Component\Core\Locale\LocaleStorageInterface;
 use Symfony\Component\HttpFoundation\RedirectResponse;
 use Symfony\Component\HttpFoundation\Request;
-use Symfony\Component\Routing\Exception\ResourceNotFoundException;
-use Symfony\Component\Routing\Matcher\UrlMatcherInterface;
+use Symfony\Component\Routing\RouterInterface;

 final class StorageBasedLocaleSwitcher implements LocaleSwitcherInterface
 {
     public function __construct(
         private LocaleStorageInterface $localeStorage,
         private ChannelContextInterface $channelContext,
-        private ?UrlMatcherInterface $urlMatcher = null,
+        private RouterInterface $router,
     ) {
-        if (null === $this->urlMatcher) {
-            trigger_deprecation(
-                'sylius/shop-bundle',
-                '2.1',
-                'Not passing a "%s" to "%s" is deprecated and will be required in Sylius 3.0.',
-                UrlMatcherInterface::class,
-                self::class,
-            );
-        }
     }

     public function handle(Request $request, string $localeCode): RedirectResponse
     {
         $this->localeStorage->set($this->channelContext->getChannel(), $localeCode);
-        $url = $request->headers->get('referer', $request->getSchemeAndHttpHost());
-
-        if ($this->urlMatcher) {
-            try {
-                $this->urlMatcher->match($url);
-            } catch (ResourceNotFoundException) {
-                return new RedirectResponse($request->getSchemeAndHttpHost());
-            }
-        }
-
-        return new RedirectResponse($url);
+        return new RedirectResponse($this->router->generate('sylius_shop_homepage'));
     }
 }
```

#### Step 4 - Override the services

Add to `config/services.yaml`.

**Sylius 1.x (1.9 – 1.14):**

```yaml
services:
    # ... your existing services ...

    sylius.controller.shop.currency_switch:
        class: App\Controller\CurrencySwitchController
        public: true
        arguments:
            $templatingEngine: '@twig'
            $currencyStorage: '@sylius.storage.currency'
            $channelContext: '@sylius.context.channel'
            $router: '@router'

    sylius.controller.shop.impersonate_user:
        class: App\Controller\Admin\ImpersonateUserController
        public: true
        arguments:
            $impersonator: '@sylius.admin.security.user_impersonator'
            $authorizationChecker: '@security.authorization_checker'
            $userProvider: '@sylius.admin_user_provider.email_or_name_based'
            $router: '@router'
            $authorizationRole: 'ROLE_ADMINISTRATION_ACCESS'

    # Only if you use locale_switcher: storage
    sylius.shop.locale_switcher:
        class: App\Locale\StorageBasedLocaleSwitcher
        public: false
        arguments:
            $localeStorage: '@sylius.storage.locale'
            $channelContext: '@sylius.context.channel'
            $router: '@router'
```

**Sylius 2.x (2.0 – 2.1):**

```yaml
services:
    # ... your existing services ...

    sylius_shop.controller.currency_switch:
        class: App\Controller\CurrencySwitchController
        public: true
        arguments:
            $currencyStorage: '@sylius.storage.currency'
            $channelContext: '@sylius.context.channel'
            $router: '@router'

    sylius_admin.controller.impersonate_user:
        class: App\Controller\Admin\ImpersonateUserController
        public: true
        arguments:
            $impersonator: '@sylius_admin.security.shop_user_impersonator'
            $authorizationChecker: '@security.authorization_checker'
            $userProvider: '@sylius.shop_user_provider.email_or_name_based'
            $router: '@router'
            $authorizationRole: 'ROLE_ADMINISTRATION_ACCESS'

    # Only if you use locale_switcher: storage
    sylius_shop.locale_switcher:
        class: App\Locale\StorageBasedLocaleSwitcher
        public: false
        arguments:
            $localeStorage: '@sylius.storage.locale'
            $channelContext: '@sylius.context.channel'
            $router: '@router'
```

#### Step 5 - Clear cache

```bash
bin/console cache:clear
```

---

#### Customizing the redirect target

If you need a different redirect target, override the route definition with the `_sylius.redirect` attribute:

```yaml
# config/routes/sylius_shop.yaml (AFTER the sylius_shop resource import)
sylius_shop_switch_currency:
    path: /{_locale}/switch-currency/{code}
    methods: [GET]
    defaults:
        _controller: sylius.controller.shop.currency_switch:switchAction
        _sylius:
            redirect: sylius_shop_product_index  # or any route name
```

### Reporters

We would like to extend our gratitude to the following individuals for their detailed reporting and responsible disclosure of this vulnerability:
- Bartłomiej Nowiński (@bnBart)

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues?q=sort%3Aupdated-desc+is%3Aissue+is%3Aopen)
- Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-9ffx-f77r-756w
- https://nvd.nist.gov/vuln/detail/CVE-2026-31819
- https://github.com/Sylius/Sylius
