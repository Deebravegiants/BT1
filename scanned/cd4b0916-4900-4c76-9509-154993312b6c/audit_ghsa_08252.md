# [M] SimpleSAMLphp casserver: Open Redirect in logout

## Summary
Severity: Medium
Advisory: GHSA-cvrm-5hp6-h523
CVE: CVE-2025-65954
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-cvrm-5hp6-h523
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp-module-casserver` — affected >=7.0.0-rc1 <7.0.0
- Packagist: `simplesamlphp/simplesamlphp-module-casserver` — affected >=0 <6.3.1

## Details
### Summary

The logout endpoint accepts a `url` query parameter to redirect to.  casserver treats that url as trusted, and either (depending on configuration) redirects the browser there, or shows a "you've been logged out" page with a link to continue to that url.

There are a number of other things broken with logout in 7 (cas v3 uses a different query parameters, etc)

### Details

https://github.com/simplesamlphp/simplesamlphp-module-casserver/blob/21418f7efbea8c4f078fd4a7d1b9eacf94dd4941/src/Controller/LogoutController.php#L104

Previous module checked the url against the valid service urls.

### PoC

The docker instructions from the README.md run an image with a vulnerable config. 

Accessing  https://localhost/cas/logout?url=https://google.com  will redirect to Google

### Impact

Impacted configs have

```php
'enable_logout' => true,
```

and are most impacted if they also have

```
'skip_logout_page' -> true,
```

## References
- https://github.com/simplesamlphp/simplesamlphp-module-casserver/security/advisories/GHSA-cvrm-5hp6-h523
- https://nvd.nist.gov/vuln/detail/CVE-2025-65954
- https://github.com/simplesamlphp/simplesamlphp-module-casserver/commit/0462f50f00b3bb300d83067d11b74146a57bb8e0
- https://github.com/simplesamlphp/simplesamlphp-module-casserver/commit/fb6c6f1c7b9e757c93c5c306e1d36405e64f6dc5
- https://github.com/simplesamlphp/simplesamlphp-module-casserver
- https://github.com/simplesamlphp/simplesamlphp-module-casserver/blob/21418f7efbea8c4f078fd4a7d1b9eacf94dd4941/src/Controller/LogoutController.php#L104
