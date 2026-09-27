# [C] Remote Code Execution Vulnerability in Validation Placeholders in CodeIgniter4

## Summary
Severity: Critical
Advisory: GHSA-m6m8-6gq8-c9fj
CVE: CVE-2023-32692
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-22
Source: https://github.com/advisories/GHSA-m6m8-6gq8-c9fj
Type: github-advisory

## Affected
- Packagist: `codeigniter4/framework` — affected >=0 <4.3.5

## Details
### Impact
This vulnerability allows attackers to execute arbitrary code when you use Validation Placeholders.

The vulnerability exists in the Validation library, and validation methods in the controller and in-model validation are also vulnerable because they use the Validation library internally.

### Patches
Upgrade to v4.3.5 or later.

### Workarounds
Setting validation rules with an array.

E.g.:
```php
$validation->setRules([
    'email' => ['required', 'valid_email, 'is_unique[users.email,id,{id}]'],
]);
```

### References
- https://codeigniter4.github.io/userguide/libraries/validation.html#validation-placeholders
- https://codeigniter4.github.io/userguide/incoming/controllers.html#validating-data
- https://codeigniter4.github.io/userguide/models/model.html#in-model-validation

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [codeigniter4/CodeIgniter4](https://github.com/codeigniter4/CodeIgniter4/issues)
* Email us at [SECURITY.md](https://github.com/codeigniter4/CodeIgniter4/blob/develop/SECURITY.md)

## References
- https://github.com/codeigniter4/CodeIgniter4/security/advisories/GHSA-m6m8-6gq8-c9fj
- https://nvd.nist.gov/vuln/detail/CVE-2023-32692
- https://github.com/codeigniter4/CodeIgniter4/commit/6af677177fa1d9ad62f7a793bc96cba3068632ba
- https://github.com/codeigniter4/CodeIgniter4
- https://github.com/codeigniter4/CodeIgniter4/blob/develop/CHANGELOG.md
- https://github.com/codeigniter4/CodeIgniter4/blob/develop/CHANGELOG.md#v435-2023-05-21
