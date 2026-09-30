# [M] BIT-nextcloud-2021-22905

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2021-22905
Aliases: CVE-2021-22905, GHSA-22v9-q3r6-x7cj
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2021-22905
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <3.16.0

## Details
Nextcloud Android App (com.nextcloud.client) before v3.16.0 is vulnerable to information disclosure due to searches for sharees being performed by default on the lookup server instead of only using the local Nextcloud server unless a global search has been explicitly chosen by the user.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-22v9-q3r6-x7cj
- https://hackerone.com/reports/1167916
- https://nvd.nist.gov/vuln/detail/CVE-2021-22905
