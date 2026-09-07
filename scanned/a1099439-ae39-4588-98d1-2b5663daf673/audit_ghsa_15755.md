# [M] ShopXO Server-Side Request Forgery Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-c96r-38gv-grp4
CVE: CVE-2024-6524
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-05
Source: https://github.com/advisories/GHSA-c96r-38gv-grp4
Type: github-advisory

## Affected
- Packagist: `shopxo/shopxo` — affected >=0

## Details
A vulnerability was found in ShopXO up to 6.1.0. It has been declared as critical. Affected by this vulnerability is an unknown functionality of the file `extend/base/Uploader.php`. The manipulation of the argument source leads to server-side request forgery. The attack can be launched remotely. The exploit has been disclosed to the public and may be used. The associated identifier of this vulnerability is VDB-270367. NOTE: The original disclosure confuses CSRF with SSRF.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6524
- https://github.com/J1rrY-learn/learn/blob/main/shopxo_ssrf.md
- https://github.com/gongfuxiang/shopxo
- https://vuldb.com/?ctiid.270367
- https://vuldb.com/?id.270367
- https://vuldb.com/?submit.365173
