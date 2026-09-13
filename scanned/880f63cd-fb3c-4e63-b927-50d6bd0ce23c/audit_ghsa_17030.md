# [H] Server-Side Template Injection (SSTI) with Grav CMS security sandbox bypass

## Summary
Severity: High
Advisory: GHSA-c9gp-64c4-2rrh
CVE: CVE-2024-28116
CWE: CWE-1336, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-c9gp-64c4-2rrh
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.45

## Details
### Summary
Grav CMS is vulnerable to a Server-Side Template Injection (SSTI), which allows any authenticated user (editor permissions are sufficient) to execute arbitrary code on the remote server bypassing the existing security sandbox.

### Details
The Grav CMS implements a custom sandbox to protect the powerful Twig methods "registerUndefinedFunctionCallback()" and "registerUndefinedFilterCallback()", in order to avoid SSTI attacks by denying the calling of dangerous PHP functions into the Twig template directives (such as: "exec()", "passthru()", "system()", etc.). 
The current defenses are based on a blacklist of prohibited functions (PHP, Twig), checked through the "isDangerousFunction()" method called in the file "system/src/Grav/Common/Twig.php":

```php
...
$this->twig = new TwigEnvironment($loader_chain, $params);

$this->twig->registerUndefinedFunctionCallback(function (string $name) use ($config) {
    $allowed = $config->get('system.twig.safe_functions');
    if (is_array($allowed) && in_array($name, $allowed, true) && function_exists($name)) {
        return new TwigFunction($name, $name);
    }
    if ($config->get('system.twig.undefined_functions')) {
        if (function_exists($name)) {
            if (!Utils::isDangerousFunction($name)) {
                user_error("PHP function {$name}() was used as Twig function. This is deprecated in Grav 1.7. Please add it to system configuration: `system.twig.safe_functions`", E_USER_DEPRECATED);

                return new TwigFunction($name, $name);
            }

           /** @var Debugger $debugger */
           $debugger = $this->grav['debugger'];
           $debugger->addException(new RuntimeException("Blocked potentially dangerous PHP function {$name}() being used as Twig function. If you really want to use it, please add it to system configuration: `system.twig.safe_functions`"));
        }

        return new TwigFunction($name, static function () {});
    }

    return false;
});

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
...
```
In the code above it can be seen that the calls of the "isDangerousFunction()" are not performed when the method/filter in the "$name" variable has been considered safe. A function can be defined safe only by an administrator user, by adding it into the configuration properties "system.twig.safe_functions" and/or "system.twig.safe_filters" (a sort of whitelists that by default are empty) of the configuration file "system/config/system.yaml".

It is to note that within the "system/src/Grav/Common/Twig.php" file a Twig class is defined (with its constructor, methods and attributes) and in particular the Twig object (and environment) is instantiated on it:
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
...
   /**
     * Constructor
     *
     * @param Grav $grav
     */
    public function __construct(Grav $grav)
    {
        $this->grav = $grav;
        $this->twig_paths = [];
    }

    /**
     * Twig initialization that sets the twig loader chain, then the environment, then extensions
     * and also the base set of twig vars
     *
     * @return $this
     */
    public function init()
    {
        if (null === $this->twig) {
            /** @var Config $config */
            $config = $this->grav['config'];
...
```
Since the security sandbox does not protect the Twig object it is possible to interact with it (e.g. call its methods, read/write its attributes) through opportunely crafted Twig template directives injected on a web page. 
Then an authenticated editor user could be able to add arbitrary functions into the Twig attributes "system.twig.safe_functions" and "system.twig.safe_filters" in order to circumvent the Grav CMS sandbox.


### PoC
An authenticated user with the permissions to edit a page (having Twig processing enabled) on the Grav CMS admin console, could create/edit a web page containing a malicious template directive to execute arbitrary OS commands on the remote web server.
For instance, in order to abuse the vulnerability and execute the prohibited "system('id')" code, bypassing the sandbox, the editor could generate a web page containing the following template directives:
```
{% set arr = {'1':'system', '2':'foo'} %}
{{ var_dump(grav.twig.twig_vars['config'].set('system.twig.safe_functions', arr)) }}
{{ system('id') }}
```
Once saved the malicious page could be accessed by unauthenticated users to execute the "system('id')" code on the remote server hosting the vulnerable Grav CMS.


### Impact
It is possible to execute remote code on the underlying server and compromise it.


### Tested version
Grav CMS v1.7.43


### Reported by
Maurizio Siddu

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-c9gp-64c4-2rrh
- https://nvd.nist.gov/vuln/detail/CVE-2024-28116
- https://github.com/getgrav/grav/commit/4149c81339274130742831422de2685f298f3a6e
- https://github.com/getgrav/grav
