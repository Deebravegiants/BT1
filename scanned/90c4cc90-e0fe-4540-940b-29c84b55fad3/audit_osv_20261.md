# [M] CVE-2021-32644

## Summary
Severity: Medium
Advisory: CVE-2021-32644
Aliases: GHSA-vqpj-xgw2-r54q
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-06-22
Source: https://osv.dev/vulnerability/CVE-2021-32644
Type: osv

## Details
Ampache is an open source web based audio/video streaming application and file manager. Due to a lack of input filtering versions 4.x.y are vulnerable to code injection in random.php. The attack requires user authentication to access the random.php page unless the site is running in demo mode. This issue has been resolved in 4.4.3.

## References
- https://github.com/ampache/ampache/security/advisories/GHSA-vqpj-xgw2-r54q
- https://github.com/ampache/ampache/commit/c9453841e1b517a1660c3da1efd1fe5d623c93a5
