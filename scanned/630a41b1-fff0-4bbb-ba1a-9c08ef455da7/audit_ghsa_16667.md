# [M] SimpleSAMLphp Information Disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-ppm4-r2vc-pg74
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-ppm4-r2vc-pg74
Type: github-advisory

## Affected
- Packagist: `simplesamlphp/simplesamlphp` — affected >=1.17.0 <1.17.8

## Details
### Background
SimpleSAMLphp 1.17 includes a preview of the new user interface to be included in the future version 2.0. This new user interface can be enabled by setting the usenewui configuration option to true, and it includes a new admin interface in a module called admin, which can be disabled.

### Description
The new admin interface includes a way to view information about the host where SimpleSAMLphp is installed, by means of the phpinfo() PHP function. An endpoint that exposes the output of that function is included in the admin module for easier debugging.

The aforementioned endpoint had no checks for administrator privileges. This would allow any individual to access the given endpoint without authenticating, gathering information about the affected system.

### Affected versions
All SimpleSAMLphp 1.17 versions up to 1.17.7 are affected, provided that the new, experimental use interface is enabled, together with the new admin module.

### Impact
An attacker could leverage this issue by accessing the unprotected endpoint and gather intelligence about the host where SimpleSAMLphp is deployed, using it later for their own advantage in case other issues arise.

However, the impact of this issue is deemed as low, given that the new user interface must be explicitly enabled by means of the usenewui configuration option, and the new admin module must also be enabled.

### Resolution
Upgrade to SimpleSAMLphp 1.17.8 or 1.18. This can be done by downloading the package, or by running composer update. Refer to the documentation for instructions on how to run composer.

Alternatively, the issue can be mitigated by either disabling the new user interface by setting the usenewui configuration option to false, or by disabling the admin module in the configuration:
```
    'module.enable' => [
        ...
        'admin' => false,
        ...
    ],
```

## References
- https://github.com/simplesamlphp/simplesamlphp/commit/0e0d1f745f5491f9e848b1f3e6da198596bb8885
- https://github.com/FriendsOfPHP/security-advisories/blob/master/simplesamlphp/simplesamlphp/2019-11-19.yaml
- https://simplesamlphp.org/security/201911-02
