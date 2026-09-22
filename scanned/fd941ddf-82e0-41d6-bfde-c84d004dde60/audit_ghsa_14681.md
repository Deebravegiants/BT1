# [H] Laravel Pulse Allows Remote Code Execution via Unprotected Query Method

## Summary
Severity: High
Advisory: GHSA-8vwh-pr89-4mw2
CVE: CVE-2024-55661
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-13
Source: https://github.com/advisories/GHSA-8vwh-pr89-4mw2
Type: github-advisory

## Affected
- Packagist: `laravel/pulse` — affected >=0 <1.3.1

## Details
A vulnerability has been discovered in Laravel Pulse that could allow remote code execution through the public `remember()` method in the `Laravel\Pulse\Livewire\Concerns\RemembersQueries` trait. This method is accessible via Livewire components and can be exploited to call arbitrary callables within the application. 

### Impact

An authenticated user with access to Laravel Pulse dashboard can execute arbitrary code by calling any function or static method that meets the following criteria:

- The callable is a function or static method
- The callable has no parameters or no strict parameter types

### Vulnerable Components

- The `remember(callable $query, string $key = '')` method in `Laravel\Pulse\Livewire\Concerns\RemembersQueries`
- Affects all Pulse card components that use this trait

### Attack Vectors

The vulnerability can be exploited through Livewire component interactions, for example:

```php
wire:click="remember('\\Illuminate\\Support\\Facades\\Config::all', 'config')"
```

### Credit

Thank you to Jeremy Angele for reporting this vulnerability.

## References
- https://github.com/laravel/pulse/security/advisories/GHSA-8vwh-pr89-4mw2
- https://nvd.nist.gov/vuln/detail/CVE-2024-55661
- https://github.com/laravel/pulse/commit/d1a5bf2eca36c6e3bedb4ceecd45df7d002a1ebc
- https://github.com/laravel/pulse
