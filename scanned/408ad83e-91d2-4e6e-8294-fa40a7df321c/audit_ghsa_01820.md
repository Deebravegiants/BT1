# [M] Laravel Framework XSS in Blade templating engine

## Summary
Severity: Medium
Advisory: GHSA-66hf-2p6w-jqfw
CVE: CVE-2021-43808
CWE: CWE-327, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-08
Source: https://github.com/advisories/GHSA-66hf-2p6w-jqfw
Type: github-advisory

## Affected
- Packagist: `laravel/framework` — affected >=0 <6.20.42
- Packagist: `laravel/framework` — affected >=7.0.0 <7.30.6
- Packagist: `laravel/framework` — affected >=8.0.0 <8.75.0
- Packagist: `illuminate/view` — affected >=0 <6.20.42
- Packagist: `illuminate/view` — affected >=7.0.0 <7.30.6
- Packagist: `illuminate/view` — affected >=8.0.0 <8.75.0

## Details
A security researcher has disclosed a possible XSS vulnerability in the Blade templating engine.

Given the following two Blade templates:

resources/views/parent.blade.php:

```html
@section('content')
<input value="{{ $value }}">
@show
```

resources/views/child.blade.php:

```html
@extends('parent')

@section('content')
<input value="{{ $value }}">
@endsection
```

And a route like the following:

```php
Route::get('/example', function() {
    $value = '//localhost/###parent-placeholder-040f06fd774092478d450774f5ba30c5da78acc8## onclick=location.assign(this.value);//';

    return view('child', ['value' => $value]);
});
```

The broken HTML element may be clicked and the user is taken to another location in their browser due to XSS. This is due to the user being able to guess the parent placeholder SHA-1 hash by trying common names of sections. If the parent template contains an exploitable HTML structure an XSS vulnerability can be exposed.

This vulnerability has been patched by determining the parent placeholder at runtime and using a random hash that is unique to each request.

## References
- https://github.com/laravel/framework/security/advisories/GHSA-66hf-2p6w-jqfw
- https://nvd.nist.gov/vuln/detail/CVE-2021-43808
- https://github.com/laravel/framework/pull/39906
- https://github.com/laravel/framework/pull/39908
- https://github.com/laravel/framework/pull/39909
- https://github.com/laravel/framework/commit/b8174169b1807f36de1837751599e2828ceddb9b
- https://github.com/FriendsOfPHP/security-advisories/blob/master/illuminate/view/CVE-2021-43808.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/laravel/framework/CVE-2021-43808.yaml
- https://github.com/laravel/framework
- https://github.com/laravel/framework/releases/tag/v6.20.42
- https://github.com/laravel/framework/releases/tag/v7.30.6
- https://github.com/laravel/framework/releases/tag/v8.75.0
