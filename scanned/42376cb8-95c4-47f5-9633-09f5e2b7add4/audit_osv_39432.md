# [H] CubeCart: Authenticated RCE via Invoice Template → Order Print

## Summary
Severity: High
Advisory: CVE-2026-45708
Aliases: GHSA-747j-4mmc-cj63
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-45708
Type: osv

## Details
CubeCart is an ecommerce software solution. Prior to 6.7.3, an admin with documents edit permission can save raw <?php … ?> into the Invoice Editor. The next time any admin clicks Print on any order, the rendered template is written to files/print.<md5>.php. files/.htaccess ships an explicit <Files print.*.php> allow from all </Files> carve-out, so the file is fetched and executed by any unauthenticated visitor. This vulnerability is fixed in 6.7.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45708.json
- https://github.com/cubecart/v6/security/advisories/GHSA-747j-4mmc-cj63
- https://nvd.nist.gov/vuln/detail/CVE-2026-45708
