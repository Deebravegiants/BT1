# [H] Unauthenticated File Read in PHP Proxy

## Summary
Severity: High
Advisory: GHSA-3x3m-p2wx-g7cw
CVE: CVE-2018-19458
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-3x3m-p2wx-g7cw
Type: github-advisory

## Affected
- Packagist: `athlon1600/php-proxy-app` — affected >=0

## Details
In PHP Proxy 3.0.3, any user can read files from the server without authentication due to an `index.php?q=file:///` LFI URI, a different vulnerability than CVE-2018-19246.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19458
- https://pentest.com.tr/exploits/PHP-Proxy-3-0-3-Local-File-Inclusion.html
- https://www.exploit-db.com/exploits/45780
