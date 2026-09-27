# [M] BIT-nextcloud-2021-22912

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2021-22912
Aliases: CVE-2021-22912, GHSA-m7w4-cvjr-76mh
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2021-22912
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <3.4.2

## Details
Nextcloud iOS before 3.4.2 suffers from an information disclosure vulnerability when searches for sharees utilize the lookup server by default instead of only on the local Nextcloud server unless a global search has been explicitly chosen by the user.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-m7w4-cvjr-76mh
- https://hackerone.com/reports/1167919
- https://nvd.nist.gov/vuln/detail/CVE-2021-22912
