# [H] Pimcore RCE via PHAR upload

## Summary
Severity: High
Advisory: GHSA-352x-hc2f-fwff
CVE: CVE-2019-16317
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-352x-hc2f-fwff
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <5.7.1

## Details
In Pimcore before 5.7.1, an attacker with limited privileges can trigger execution of a .phar file via a `phar://` URL in a filename parameter, because PHAR uploads are not blocked and are reachable within the `phar://../../../../../../../../var/www/html/web/var/assets/` directory, a different vulnerability than CVE-2019-10867 and CVE-2019-16318.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16317
- https://github.com/pimcore/pimcore/commit/6ee5d8536d0802e377594cbe39083e822710aab9
- https://snyk.io/vuln/SNYK-PHP-PIMCOREPIMCORE-451599
