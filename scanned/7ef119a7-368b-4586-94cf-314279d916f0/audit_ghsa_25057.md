# [M] Cosenary Instagram-PHP-API contains reflected XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gcv6-2v9c-rj48
CVE: CVE-2019-14470
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gcv6-2v9c-rj48
Type: github-advisory

## Affected
- Packagist: `cosenary/instagram` — affected >=0

## Details
cosenary Instagram-PHP-API (aka Instagram PHP API V2), used in the UserPro plugin through 4.9.32 for WordPress, is vulnerable to cross-site scripting via the [example/success.php](https://github.com/cosenary/Instagram-PHP-API/blob/master/example/success.php#L36
) error_description parameter.

Vulnerable code:

```php
    if (isset($_GET['error'])) {
        echo 'An error occurred: ' . $_GET['error_description'];
    }
```

Proof-of-Concept:

`https://domain.tld/wp-content/plugins/userpro/lib/instagram/vendor/cosenary/instagram/example/success.php?error=&error_description=<PAYLOAD>`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-14470
- https://github.com/cosenary/Instagram-PHP-API
- https://github.com/cosenary/Instagram-PHP-API/blob/master/example/success.php#L33-L36
- https://wpvulndb.com/vulnerabilities/9815
- https://www.exploit-db.com/exploits/47304
- http://packetstormsecurity.com/files/154206/WordPress-UserPro-4.9.32-Cross-Site-Scripting.html
