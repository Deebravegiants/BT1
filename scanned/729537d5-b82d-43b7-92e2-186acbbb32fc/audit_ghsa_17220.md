# [H] Grav is Vulnerable to Security Sandbox Bypass with SSTI (Server Side Template Injection)

## Summary
Severity: High
Advisory: GHSA-gjc5-8cfh-653x
CVE: CVE-2025-66299
CWE: CWE-1336, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-gjc5-8cfh-653x
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
## Summary

Grav CMS is vulnerable to a Server-Side Template Injection (SSTI) that allows any authenticated user with editor permissions to execute arbitrary code on the remote server, bypassing the existing security sandbox.

## Details

Grav CMS uses a custom sandbox to protect the powerful Twig methods such as `registerUndefinedFilterCallback()`. These methods are designed to prevent SSTI attacks by denying the execution of dangerous PHP functions (e.g., `exec()`, `passthru()`, `system()`, etc.) within Twig template directives.

The current defense mechanism relies on a blacklist of prohibited functions (PHP, Twig), checked through the `isDangerousFunction()` method in the file `system/src/Grav/Common/Twig.php`:

```php
$this->twig->registerUndefinedFilterCallback(function (string $name) use ($config) {
    $allowed = $config->get('system.twig.safe_filters');
    if (is_array($allowed) && in_array($name, $allowed, true) && function_exists($name)) {
        return new TwigFilter($name, $name);
    }
    if ($config->get('system.twig.undefined_filters')) {
        if (function_exists($name)) {
            if (!Utils::isDangerousFunction($name)) {
                user_error("PHP function {$name}() used as Twig filter. This is deprecated in Grav 1.7. Please add it to system configuration: `system.twig.safe_filters`", E_USER_DEPRECATED);

                return new TwigFilter($name, $name);
            }

            /** @var Debugger $debugger */
            $debugger = $this->grav['debugger'];
            $debugger->addException(new RuntimeException("Blocked potentially dangerous PHP function {$name}() being used as Twig filter. If you really want to use it, please add it to system configuration: `system.twig.safe_filters`"));
        }

        return new TwigFilter($name, static function () {});
    }

    return false;
});
```

In this code, the `isDangerousFunction()` check is bypassed if the filter defined in the $name variable is considered safe. Only an administrator can mark a function as safe by adding it to the `system.twig.safe_filters` configuration properties (whitelists that are empty by default) in the `system/config/system.yaml` file.

Notably, the Twig class is defined within the `system/src/Grav/Common/Twig.php` file, and the Twig object (and environment) is instantiated there:

```php
/**
 * Class Twig
 * @package Grav\Common\Twig
 */
class Twig
{
    /** @var Environment */
    public $twig;
    /** @var array */
    public $twig_vars = [];
    /** @var array */
    public $twig_paths;
    /** @var string */
    public $template;

    // Constructor
    public function __construct(Grav $grav)
    {
        $this->grav = $grav;
        $this->twig_paths = [];
    }

    // Twig initialization method
    public function init()
    {
        if (null === $this->twig) {
            /** @var Config $config */
            $config = $this->grav['config'];
            /** @var UniformResourceLocator $locator */
            $locator = $this->grav['locator'];
            /** @var Language $language */
            $language = $this->grav['language'];

            $active_language = $language->getActive();
        ...
        }
    }
}
```

Since the security sandbox does not fully protect the Twig object, it is possible to interact with it (e.g., call methods, read/write attributes) through maliciously crafted Twig template directives injected into a web page. This allows an authenticated editor to add arbitrary functions to the Twig attribute `system.twig.safe_filters`, effectively bypassing the Grav CMS sandbox.

## Proof of Concept (PoC)
An authenticated user with permission to edit a page (with Twig processing enabled) in the Grav CMS admin console can inject malicious template directives to execute arbitrary OS commands on the remote web server.

For example, to exploit the vulnerability and execute the prohibited `system('id')` command, bypassing the sandbox, an editor could create/edit a web page with the following template directives:

```twig
{% set arr = {'1':'system', '2':'exec'} %}
{{ var_dump(grav.twig.twig_vars['config'].set('system.twig.safe_filters', arr)) }}
{{ 'id'|system }}
{{ 'whoami'|exec }}
```

Once the page is saved, it can be accessed by unauthenticated users, triggering the execution of the `system('id')` command on the server hosting the vulnerable Grav CMS.

## Impact
The vulnerability allows remote code execution on the underlying server, which could lead to full server compromise.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-gjc5-8cfh-653x
- https://nvd.nist.gov/vuln/detail/CVE-2025-66299
- https://github.com/getgrav/grav/commit/e37259527d9c1deb6200f8967197a9fa587c6458
- https://github.com/getgrav/grav
