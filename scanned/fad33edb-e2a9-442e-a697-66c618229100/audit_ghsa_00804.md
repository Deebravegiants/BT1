# [H] Remote Code Execution in SyliusResourceBundle

## Summary
Severity: High
Advisory: GHSA-p4pj-9g59-4ppv
CVE: CVE-2020-15143
CWE: CWE-74, CWE-917
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2020-08-19
Source: https://github.com/advisories/GHSA-p4pj-9g59-4ppv
Type: github-advisory

## Affected
- Packagist: `sylius/resource-bundle` — affected >=1.4.0 <1.4.7
- Packagist: `sylius/resource-bundle` — affected >=1.5.0 <1.5.2
- Packagist: `sylius/resource-bundle` — affected >=1.6.0 <1.6.4
- Packagist: `sylius/resource-bundle` — affected >=1.0.0 <1.3.14

## Details
### Impact

Request parameters injected inside an expression evaluated by `symfony/expression-language` package haven't been sanitized properly. This allows the attacker to access any public service by manipulating that request parameter, allowing for Remote Code Execution.

The vulnerable versions include: `<=1.3.13 || >=1.4.0 <=1.4.6 || >=1.5.0 <=1.5.1 || >=1.6.0 <=1.6.3`.

### Example

```yaml
foo:
    path: /foo/{id}
    defaults:
        _sylius:
            repository:
                method: findSome
                arguments:
                    entity: "expr:service('repository').find($id)"
```

In this case, `$id` can be prepared in a way that calls other services. 

If you visit `/foo/"~service('doctrine').getManager().getConnection().executeQuery("DELETE * FROM TABLE")~"`, it will result in a following expression `expr:service('repository').find(""~service('doctrine').getManager().getConnection().executeQuery("DELETE * FROM TABLE")~"")`, which will execute a query on the currently connected database.

To find a vulnerability in your application, look for any routing definition that uses request parameters inside expression language.

### Patches

This issue has been patched for versions 1.3.14, 1.4.7, 1.5.2 and 1.6.4. Versions prior to 1.3 were not patched.

### Workarounds

The fix requires adding `addslashes` in `ParametersParser::parseRequestValueExpression` to sanitize user input before evaluating it using the expression language.

```php
- return is_string($variable) ? sprintf('"%s"', $variable) : $variable;
+ return is_string($variable) ? sprintf('"%s"', addslashes($variable)) : $variable;
```

### Acknowledgements

This security issue has been reported by Craig Blanchette (@isometriks), thanks a lot!

### For more information

If you have any questions or comments about this advisory:
* Email us at [security@sylius.com](mailto:security@sylius.com)

## References
- https://github.com/Sylius/SyliusResourceBundle/security/advisories/GHSA-p4pj-9g59-4ppv
- https://nvd.nist.gov/vuln/detail/CVE-2020-15143
- https://github.com/Sylius/SyliusResourceBundle/commit/73ed8b8bb083f36c30ad7c3cec336f65d6a80650
- https://github.com/FriendsOfPHP/security-advisories/blob/master/sylius/resource-bundle/CVE-2020-15143.yaml
- https://github.com/Sylius/SyliusResourceBundle
