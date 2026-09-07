# [H] Insecure Inherited Permissions in neoan3-apps/template

## Summary
Severity: High
Advisory: GHSA-3v56-q6r6-4gcw
CVE: CVE-2021-41170
CWE: CWE-277, CWE-732, CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-11-10
Source: https://github.com/advisories/GHSA-3v56-q6r6-4gcw
Type: github-advisory

## Affected
- Packagist: `neoan3-apps/template` — affected >=0 <1.1.1

## Details
### Impact
Versions prior 1.1.1 have allowed for passing in closures directly into the template engine. As a result values that are callable are executed by the template engine. The issue arises if a value has the same name as a method or function in scope and can therefore be executed either by mistake or maliciously. 

In theory all users of the package are affected as long as they either deal with direct user input or database values. A multi-step attack on is therefore plausible. 


### Patches
Version 1.1.1 has addressed this vulnerability. 
```php
$params = [
   'reverse' => fn($input) => strrev($input),    // <-- no longer possible with version ~1.1.1
   'value' => 'My website' 
]
TemplateFunctions::registerClosure('reverse', fn($input) => strrev($input));  // <-- still possible (and nicely isolated)
Template::embrace('<h1>{{reverse(value)}}</h1>', $params);
```

### Workarounds
Unfortunately only working with hardcoded values is safe in prior versions. As this likely defeats the purpose of a template engine, please upgrade.

### References
As a possible exploit is relatively easy to achieve, I will not share steps to reproduce the issue for now.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [our repo](https://github.com/sroehrl/neoan3-template)

## References
- https://github.com/sroehrl/neoan3-template/security/advisories/GHSA-3v56-q6r6-4gcw
- https://nvd.nist.gov/vuln/detail/CVE-2021-41170
- https://github.com/sroehrl/neoan3-template/issues/8
- https://github.com/sroehrl/neoan3-template/commit/4a2c9570f071d3c8f4ac790007599cba20e16934
- https://github.com/sroehrl/neoan3-template
