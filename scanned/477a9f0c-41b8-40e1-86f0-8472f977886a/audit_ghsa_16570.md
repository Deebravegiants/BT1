# [M] Laravel Encrypter Component Potential Decryption Failure Leading to Unintended Behavior

## Summary
Severity: Medium
Advisory: GHSA-7852-w36x-6mf6
CWE: CWE-1240
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-7852-w36x-6mf6
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=0 <5.5.40
- Packagist: `laravel/framework` — affected >=5.6.0 <5.6.15

## Details
The Laravel Encrypter component is susceptible to a vulnerability that may result in decryption failure, leading to an unexpected return of `false`. Exploiting this issue requires the attacker to manipulate the encrypted payload before decryption. When combined with weak type comparisons in the application's code, such as the example below:

```
<?php

$decyptedValue = decrypt($secret);

if ($decryptedValue == '') {
    // Code is run even though decrypted value is false...
}
```

## References
- https://github.com/laravel/framework/commit/28e53f23a76206fb130e9a54eb95aa3f010e79c9
- https://github.com/laravel/framework/commit/886d261df0854426b4662b7ed5db6a1c575a4279
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/2018-03-30-1.yaml
- https://github.com/laravel/framework
- https://medium.com/@taylorotwell/laravel-security-release-5-6-15-and-5-5-40-56f1257933a0
