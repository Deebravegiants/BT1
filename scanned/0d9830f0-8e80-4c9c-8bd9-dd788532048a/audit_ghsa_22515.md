# [H] LFI in PHP-Proxy 5.1.0

## Summary
Severity: High
Advisory: GHSA-pc5h-m95g-v6rh
CVE: CVE-2018-19246
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-pc5h-m95g-v6rh
Type: github-advisory

## Affected
- Packagist: `athlon1600/php-proxy` — affected >=0

## Details
PHP-Proxy 5.1.0 allows remote attackers to read local files if the default "pre-installed version" (intended for users who lack shell access to their web server) is used. This occurs because the `aeb067ca0aa9a3193dce3a7264c90187` app_key value from the default config.php is in place, and this value can be easily used to calculate the authorization data needed for local file inclusion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19246
- https://github.com/Athlon1600/php-proxy-app/issues/134
- https://github.com/Athlon1600/php-proxy/pull/126
- https://www.exploit-db.com/exploits/45861
