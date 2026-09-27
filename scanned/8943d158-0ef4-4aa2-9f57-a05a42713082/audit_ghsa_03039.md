# [H] SSRF in adminer

## Summary
Severity: High
Advisory: GHSA-x5r2-hj5c-8jx6
CVE: CVE-2021-21311
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N/E:H (CVSS_V3)
Published: 2021-02-11
Source: https://github.com/advisories/GHSA-x5r2-hj5c-8jx6
Type: github-advisory

## Affected
- Packagist: `vrana/adminer` — affected >=0 <4.7.9

## Details
### Impact
Users of Adminer versions bundling all drivers (e.g. `adminer.php`) are affected.

### Patches
Patched by ccd2374b, included in version [4.7.9](https://github.com/vrana/adminer/releases/tag/v4.7.9).

### Workarounds
* Use a single driver version (e.g. `adminer-mysql.php`).
* Protect access to Adminer also by other means, e.g. by HTTP password, IP address limiting or by OTP [plugin](https://www.adminer.org/plugins/).

### References
https://github.com/vrana/adminer/files/5957311/Adminer.SSRF.pdf

### For more information
If you have any questions or comments about this advisory:
* Comment at ccd2374b.

## References
- https://github.com/vrana/adminer/security/advisories/GHSA-x5r2-hj5c-8jx6
- https://nvd.nist.gov/vuln/detail/CVE-2021-21311
- https://github.com/vrana/adminer/commit/ccd2374b0b12bd547417bf0dacdf153826c83351
- https://github.com/vrana/adminer
- https://github.com/vrana/adminer/files/5957311/Adminer.SSRF.pdf
- https://lists.debian.org/debian-lts-announce/2021/03/msg00002.html
- https://packagist.org/packages/vrana/adminer
- https://sourceforge.net/p/adminer/news/2021/02/adminer-479-released
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-21311
