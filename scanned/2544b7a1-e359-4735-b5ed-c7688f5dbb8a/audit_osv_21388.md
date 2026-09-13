# [C] CVE-2021-4259

## Summary
Severity: Critical
Advisory: CVE-2021-4259
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-19
Source: https://osv.dev/vulnerability/CVE-2021-4259
Type: osv

## Details
A vulnerability was found in phpRedisAdmin up to 1.16.1. It has been classified as problematic. This affects the function authHttpDigest of the file includes/login.inc.php. The manipulation of the argument response leads to use of wrong operator in string comparison. Upgrading to version 1.16.2 is able to address this issue. The name of the patch is 31aa7661e6db6f4dffbf9a635817832a0a11c7d9. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-216267.

## References
- https://github.com/erikdubbelboer/phpRedisAdmin/releases/tag/v1.16.2
- https://vuldb.com/?id.216267
- https://github.com/erikdubbelboer/phpRedisAdmin/commit/31aa7661e6db6f4dffbf9a635817832a0a11c7d9
