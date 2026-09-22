# [M] CVE-2022-40482

## Summary
Severity: Medium
Advisory: CVE-2022-40482
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-04-25
Source: https://osv.dev/vulnerability/CVE-2022-40482
Type: osv

## Details
The authentication method in Laravel 8.x through 9.x before 9.32.0 was discovered to be vulnerable to user enumeration via timeless timing attacks with HTTP/2 multiplexing. This is caused by the early return inside the hasValidCredentials method in the Illuminate\Auth\SessionGuard class when a user is found to not exist.

## References
- https://github.com/laravel/framework/releases/tag/v9.32.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40482.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-40482
- https://github.com/laravel/framework/pull/44069
- https://github.com/ephort/laravel-user-enumeration-demo
- https://ephort.dk/blog/laravel-timing-attack-vulnerability/
