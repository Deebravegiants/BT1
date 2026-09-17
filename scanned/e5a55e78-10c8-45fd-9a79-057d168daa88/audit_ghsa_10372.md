# [C] goodoneuz/pay-uz: the /payment/api/editable/update endpoint overwrites existing PHP payment hook files

## Summary
Severity: Critical
Advisory: GHSA-m5wg-cjgh-223j
CVE: CVE-2026-31843
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-m5wg-cjgh-223j
Type: github-advisory

## Affected
- Packagist: `goodoneuz/pay-uz` — affected >=0 <3.0.0

## Details
The goodoneuz/pay-uz Laravel package (<= 2.2.24) contains a critical vulnerability in the /payment/api/editable/update endpoint that allows unauthenticated attackers to overwrite existing PHP payment hook files. The endpoint is exposed via Route::any() without authentication middleware, enabling remote access without credentials. User-controlled input is directly written into executable PHP files using file_put_contents(). These files are later executed via require() during normal payment processing workflows, resulting in remote code execution under default application behavior. The payment secret token mentioned by the vendor is unrelated to this endpoint and does not mitigate the vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31843
- https://github.com/shaxzodbek-uzb/pay-uz/pull/73
- https://github.com/goodoneuz/pay-uz/blob/master/src/Http/Controllers/ApiController.php
- https://github.com/goodoneuz/pay-uz/blob/master/src/routes/web.php
- https://github.com/shaxzodbek-uzb/pay-uz
- https://github.com/shaxzodbek-uzb/pay-uz/releases/tag/3.0.0
- https://packagist.org/packages/goodoneuz/pay-uz
