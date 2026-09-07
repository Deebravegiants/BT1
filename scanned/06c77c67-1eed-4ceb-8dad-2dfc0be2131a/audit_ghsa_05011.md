# [M] backpack/crud is vulnerable to Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-m8xx-3x29-84h8
CVE: CVE-2022-31114
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-m8xx-3x29-84h8
Type: github-advisory

## Affected
- Packagist: `backpack/crud` — affected >=5.0.0 <5.0.13
- Packagist: `backpack/crud` — affected >=4.1.0 <4.1.69
- Packagist: `backpack/crud` — affected >=0 <4.0.63

## Details
### Impact

It’s a “*moderate*” vulnerability… but being an admin panel, take this seriously. It’s difficult… but an attacker could conduct a targeted phishing campaign, in order to **trick your users or admins to click a malicious link, which under very specific circumstances could give them information... or even admin access**. It’s *unlikely*, but that’s not good enough in admin panels - It should be made *impossible*. That’s why you are bothered with this. 

### Patches


If you don’t have custom error views, the views provided by Backpack would output the exception message *without escaping it*, which made an attack possible using Reflected XSS, in some very specific circumstances (that we will not disclose). **To fix those error views in Backpack 4.x and 5.x, please run**:

```bash
composer update backpack/crud
php artisan backpack:fix
```

The problem has been patched in:
- v4.0.63
- v4.1.69
- v5.0.13

> **IMPORTANT! Running a `composer update` should get you the patched version, but you also need to run `php artisan backpack:fix` afterwards, to patch your published error views, if necessary.**

### Workarounds

Alternatively (if you don’t want to run `composer update`), you can manually look inside your error views in “*resources/views/errors*” and output `e($exception->getMessage())` instead of `$exception->getMessage()`. That’s all there is to the fix, really.

### What the maintainers have done about this

Acted as soon as our team found it (last week of March 2022):
- Pushed patches to 5.x, 4.1 and 4.0;
- Made it easy to apply the fix to existing projects, using a new `php artisan backpack:fix` command;
- Kept the specific circumstances a secret; as far as they know, only the maintainer's team knows about the niche case where this exploit is possible;
- Emailed all our licensed users, to have a chance to fix their projects before it’s public;
- Sent an email blast to our 25.000+ strong Security Newsletter;
- Made this public with a blog post and soon a CVE, after our community has had a reasonable chance to fix their projects;
- Will continue to monitor this and remind paying users to apply this fix if they haven’t;

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [backpack/crud](https://github.com/laravel-backpack/crud)
* Email us at [hello@backpackforlaravel.com](mailto:hello@backpackforlaravel.com)

---

PS. You can [read this blog post](https://backpackforlaravel.com/articles/news/we-recommend-you-fix-this-vulnerability) for more information.

## References
- https://github.com/Laravel-Backpack/CRUD/security/advisories/GHSA-m8xx-3x29-84h8
- https://nvd.nist.gov/vuln/detail/CVE-2022-31114
- https://backpackforlaravel.com/articles/news/we-recommend-you-fix-this-vulnerability
- https://github.com/Laravel-Backpack/CRUD
