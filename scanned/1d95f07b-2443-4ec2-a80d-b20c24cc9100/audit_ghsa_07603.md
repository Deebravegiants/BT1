# [H] Zumba Json Serializer has a potential PHP Object Injection via Unrestricted @type in unserialize()

## Summary
Severity: High
Advisory: GHSA-v7m3-fpcr-h7m2
CVE: CVE-2026-27206
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-v7m3-fpcr-h7m2
Type: github-advisory

## Affected
- Packagist: `zumba/json-serializer` — affected >=0 <3.2.3

## Details
### Description

The `zumba/json-serializer` library allows deserialization of PHP objects from JSON using a special `@type` field.

Prior to version 3.2.3, the deserializer would instantiate any class specified in the `@type` field without restriction. When processing untrusted JSON input, this behavior may allow an attacker to instantiate arbitrary classes available in the application.

If a vulnerable application passes attacker-controlled JSON into JsonSerializer::unserialize() and contains classes with dangerous magic methods (such as `__wakeup()` or `__destruct()`), this may lead to PHP Object Injection and potentially Remote Code Execution (RCE), depending on available gadget chains in the application or its dependencies.

This behavior is similar in risk profile to PHP's native `unserialize()` when used without the `allowed_classes` restriction.

### Impact

This vulnerability allows instantiation of arbitrary PHP classes via the `@type` field when deserializing JSON.

Applications are impacted only if:
* Untrusted or attacker-controlled JSON is passed into `JsonSerializer::unserialize()`, and
* The application or its dependencies contain classes that can be leveraged as a gadget chain.

Successful exploitation may lead to:
* Arbitrary code execution
* Data exfiltration
* File manipulation
* Denial of service

Applications that only deserialize trusted data are not affected.

### Patches

This issue is mitigated in version 3.2.3.

Version 3.2.3 introduces the method: `setAllowedClasses(?array $allowedClasses)`

This allows applications to restrict which classes may be instantiated during deserialization, similar to PHP's native `unserialize()` `allowed_classes` option.

Users should upgrade to version 3.2.3 or later and configure an appropriate class allowlist.

### Workarounds

If upgrading is not immediately possible, applications should ensure that:
* `JsonSerializer::unserialize()` is never called on untrusted or attacker-controlled JSON.
* JSON input is validated and sanitized before deserialization.
* Object instantiation via `@type` is disabled in application logic where possible.

After upgrading, users can mitigate risk by explicitly configuring:

```php
$serializer->setAllowedClasses([]);
```

to disable all object instantiation, or by providing a strict allowlist of safe classes.

### References

* CWE-502: https://cwe.mitre.org/data/definitions/502.html
* PHP `unserialize()` documentation: https://www.php.net/manual/en/function.unserialize.php
* OWASP PHP Object Injection: https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection

## References
- https://github.com/zumba/json-serializer/security/advisories/GHSA-v7m3-fpcr-h7m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27206
- https://github.com/zumba/json-serializer/commit/bf26227879adefce75eb9651040d8982be97b881
- https://github.com/zumba/json-serializer
- https://github.com/zumba/json-serializer/releases/tag/3.2.3
