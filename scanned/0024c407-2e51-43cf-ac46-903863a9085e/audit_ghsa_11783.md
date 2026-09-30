# [M] Sylius has a XSS vulnerability in checkout login form

## Summary
Severity: Medium
Advisory: GHSA-vgh8-c6fp-7gcg
CVE: CVE-2026-31822
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-vgh8-c6fp-7gcg
Type: github-advisory

## Affected
- Packagist: `sylius/sylius` — affected >=2.0.0 <2.0.16
- Packagist: `sylius/sylius` — affected >=2.1.0 <2.1.12
- Packagist: `sylius/sylius` — affected >=2.2.0 <2.2.3

## Details
### Impact

A cross-site scripting (XSS) vulnerability exists in the shop checkout login form handled by the ApiLoginController Stimulus controller.                                                                                                               

When a login attempt fails, AuthenticationFailureHandler returns a JSON response whose message field is rendered into the DOM using innerHTML, allowing any HTML or JavaScript in that value to be parsed and executed by the browser.

The message value originates from `AuthenticationException::getMessageKey()` passed through Symfony's translator (security domain, using the request locale). In the default Sylius installation, this returns a hardcoded translation key (e.g. "Invalid credentials."), which is not directly user-controlled. However, using innerHTML with server-derived data violates defense-in-depth principles, and the risk escalates significantly under realistic scenarios:
  - Customized authentication handlers — if a project overrides AuthenticationFailureHandler to include user-supplied data in the message (e.g. "No account found for <username>"), an attacker can inject arbitrary JavaScript directly via the login
  form without any privileged access.
  - Translation injection — if translation files are sourced from an untrusted database or CMS and contain HTML, the message could carry a malicious payload.
  - Man-in-the-Middle — if the response is intercepted (e.g. on HTTP or via a compromised proxy), an attacker can inject arbitrary HTML/JS into the message field.
  - Server-side injection — if any middleware, reverse proxy, or error handler modifies the JSON response body, malicious content could be injected into the message field.

Exploitation could lead to session hijacking, credential theft, cart/order manipulation, or phishing within the trusted shop domain.

The vulnerability affects all Sylius installations that use the default shop checkout login form with the bundled ApiLoginController.js.

### Patches
The issue is fixed in versions: 2.0.16, 2.1.12, 2.2.3 and above.

### Workarounds
Override the vulnerable JavaScript controller at the project level.
> Note: Step 2 differs between Sylius 2.0 and up

#### Step 1. Override JavaScript controller handling login
### Patch ApiLoginController.js

Copy the original from `vendor/sylius/sylius/src/Sylius/Bundle/ShopBundle/Resources/assets/controllers/ApiLoginController.js` to `assets/shop/controllers/ApiLoginController.js` and apply:
```diff
...
  .then(response => {
    if (response.success) {
      window.location.reload();
    } else {
      const errorElement = this.errorPrototypeTarget.cloneNode(true);
-     errorElement.innerHtml = response.message;
+     errorElement.textContent = response.message;
      this.errorTarget.innerHTML = errorElement.outerHTML;
    }
  })
...
```

#### Step 2. Register the patched controller
> Sylius 2.1+ (Stimulus Bridge with `controllers.json`)

Disable the vendor controller in `assets/shop/controllers.json`:
```diff
...
  "api-login": {
-    "enabled": true,
+    "enabled": false,
    "fetch": "lazy"
  }
...
```
Register the overwritten controller in `assets/shop/bootstrap.js`
```js
import ApiLoginController from './controllers/ApiLoginController'

app.register('sylius--shop-bundle--api-login', ApiLoginController);
```
---
> Sylius 2.0 (explicit imports in vendor `app.js`)

Use Webpack's `NormalModuleReplacementPlugin` to swap the controller at build time. In `webpack.config.js`, after `shopConfig` is created:

```diff
+ const webpack = require('webpack');
...
  // Shop config
  const shopConfig = SyliusShop.getWebpackConfig(path.resolve(__dirname));
+ shopConfig.plugins.push(
+   new webpack.NormalModuleReplacementPlugin(
+     /\/controllers\/ApiLoginController\.js$/,
+     path.resolve(__dirname, 'assets/shop/controllers/ApiLoginController.js')
+   )
+ );
...
```

#### Step 3. Rebuild assets

```bash
yarn encore dev  # or: yarn encore production
```

### Reporters

We would like to extend our gratitude to the following individuals for their detailed reporting and responsible disclosure of this vulnerability:
- Bartłomiej Nowiński (@bnBart)

### For more information

If you have any questions or comments about this advisory:

- Open an issue in [Sylius issues](https://github.com/Sylius/Sylius/issues?q=sort%3Aupdated-desc+is%3Aissue+is%3Aopen)
- Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/Sylius/security/advisories/GHSA-vgh8-c6fp-7gcg
- https://nvd.nist.gov/vuln/detail/CVE-2026-31822
- https://github.com/Sylius/Sylius
