# [C] Insecure Deserialization of untrusted data in rmccue/requests

## Summary
Severity: Critical
Advisory: GHSA-52qp-jpq7-6c54
CVE: CVE-2021-29476
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-29
Source: https://github.com/advisories/GHSA-52qp-jpq7-6c54
Type: github-advisory

## Affected
- Packagist: `rmccue/requests` — affected >=1.6.0 <1.8.0

## Details
### Impact
Unserialization of untrusted data.

### Patches
The issue has been patched and users of `Requests` 1.6.0, 1.6.1 and 1.7.0 should update to version 1.8.0.

### References
Publications about the vulnerability:
* https://dannewitz.ninja/posts/php-unserialize-object-injection-yet-another-stars-rating-wordpress
* https://github.com/ambionics/phpggc/issues/52
* https://blog.detectify.com/2019/07/23/improving-wordpress-plugin-security/
* https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf
* https://cdn2.hubspot.net/hubfs/3853213/us-18-Thomas-It%27s-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-....pdf
* https://2018.zeronights.ru/wp-content/uploads/materials/9%20ZN2018%20WV%20-%20PHP%20unserialize.pdf
* https://medium.com/@knownsec404team/extend-the-attack-surface-of-php-deserialization-vulnerability-via-phar-d6455c6a1066#3c0f

Originally fixed in WordPress 5.5.2:
* https://github.com/WordPress/wordpress-develop/commit/add6bedf3a53b647d0ebda2970057912d3cd79d3
* https://wordpress.org/news/2020/10/wordpress-5-5-2-security-and-maintenance-release/

Related Security Advisories:
* https://cve.mitre.org/cgi-bin/cvename.cgi?name=2020-28032
* https://nvd.nist.gov/vuln/detail/CVE-2020-28032

Notification to the Requests repo including a fix in:
* https://github.com/rmccue/Requests/pull/421 and
* https://github.com/rmccue/Requests/pull/422

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Request](https://github.com/WordPress/Requests/)

## References
- https://github.com/WordPress/Requests/security/advisories/GHSA-52qp-jpq7-6c54
- https://nvd.nist.gov/vuln/detail/CVE-2021-29476
- https://github.com/ambionics/phpggc/issues/52
- https://github.com/rmccue/Requests/pull/421
- https://github.com/WordPress/wordpress-develop/commit/add6bedf3a53b647d0ebda2970057912d3cd79d3
- https://2018.zeronights.ru/wp-content/uploads/materials/9%20ZN2018%20WV%20-%20PHP%20unserialize.pdf
- https://blog.detectify.com/2019/07/23/improving-wordpress-plugin-security
- https://cdn2.hubspot.net/hubfs/3853213/us-18-Thomas-It%27s-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-....pdf
- https://dannewitz.ninja/posts/php-unserialize-object-injection-yet-another-stars-rating-wordpress
- https://github.com/FriendsOfPHP/security-advisories/blob/master/rmccue/requests/CVE-2021-29476.yaml
- https://i.blackhat.com/us-18/Thu-August-9/us-18-Thomas-Its-A-PHP-Unserialization-Vulnerability-Jim-But-Not-As-We-Know-It.pdf
- https://medium.com/@knownsec404team/extend-the-attack-surface-of-php-deserialization-vulnerability-via-phar-d6455c6a1066#3c0f
- https://wordpress.org/news/2020/10/wordpress-5-5-2-security-and-maintenance-release
