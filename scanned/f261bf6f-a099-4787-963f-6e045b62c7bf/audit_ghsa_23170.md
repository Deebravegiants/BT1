# [H] Weak Cryptography in PHP-Proxy

## Summary
Severity: High
Advisory: GHSA-4wgf-9x5r-p938
CVE: CVE-2018-19784
CWE: CWE-326
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4wgf-9x5r-p938
Type: github-advisory

## Affected
- Packagist: `athlon1600/php-proxy` — affected >=0

## Details
The [str_rot_pass](https://github.com/Athlon1600/php-proxy/blob/9cc42804ddafa079b86b947e4dd83852edddffca/src/helpers.php#L66) function in vendor/atholn1600/php-proxy/src/helpers.php in PHP-Proxy 5.1.0 uses weak cryptography, which makes it easier for attackers to calculate the authorization data needed for local file inclusion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19784
- https://github.com/Athlon1600/php-proxy-app/issues/139
- https://github.com/0xUhaw/CVE-Bins/tree/master/PHP-Proxy
- https://github.com/Athlon1600/php-proxy
