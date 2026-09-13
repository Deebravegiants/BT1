# [C] CVE-2019-13983

## Summary
Severity: Critical
Advisory: CVE-2019-13983
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-19
Source: https://osv.dev/vulnerability/CVE-2019-13983
Type: osv

## Details
Directus 7 API before 2.2.2 has insufficient anti-automation, as demonstrated by lack of a CAPTCHA in core/Directus/Services/AuthService.php and endpoints/Auth.php.

## References
- https://github.com/directus/api/projects/43
- https://github.com/directus/api/issues/991
