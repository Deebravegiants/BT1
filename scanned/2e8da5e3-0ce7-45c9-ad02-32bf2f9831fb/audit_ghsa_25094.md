# [M] Woocommerce Cross-site Scripting via Additional tax classes field when taxes are enabled

## Summary
Severity: Medium
Advisory: GHSA-mp46-7x6q-f28m
CVE: CVE-2021-24323
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mp46-7x6q-f28m
Type: github-advisory

## Affected
- Packagist: `woocommerce/woocommerce` — affected >=0 <5.2.0

## Details
When taxes are enabled, the "Additional tax classes" field was not properly sanitised or escaped before being output back in the admin dashboard, allowing high privilege users such as admin to use XSS payloads even when the unfiltered_html is disabled

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-24323
- https://github.com/woocommerce/woocommerce/commit/6ede8c5f59aec3ca70aa27d1ffd5a6574473f2ce
- https://github.com/woocommerce/woocommerce
- https://wpscan.com/vulnerability/6d262555-7ae4-4e36-add6-4baa34dc3010
