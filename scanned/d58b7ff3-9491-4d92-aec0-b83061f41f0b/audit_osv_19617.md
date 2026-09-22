# [M] CVE-2021-22913

## Summary
Severity: Medium
Advisory: CVE-2021-22913
Aliases: GHSA-h8f6-wg82-6p7r
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2021-06-11
Source: https://osv.dev/vulnerability/CVE-2021-22913
Type: osv

## Details
Nextcloud Deck before 1.2.7, 1.4.1 suffers from an information disclosure vulnerability when searches for sharees utilize the lookup server by default instead of only the local Nextcloud server unless a global search has been explicitly chosen by the user.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-h8f6-wg82-6p7r
- https://hackerone.com/reports/1167958
