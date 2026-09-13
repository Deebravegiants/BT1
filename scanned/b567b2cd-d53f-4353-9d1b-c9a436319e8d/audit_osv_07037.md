# [M] BIT-nextcloud-2021-22896

## Summary
Severity: Medium
Advisory: BIT-nextcloud-2021-22896
Aliases: CVE-2021-22896, GHSA-jmgp-77jq-fjp3
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2021-22896
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <1.9.5

## Details
Nextcloud Mail before 1.9.5 suffers from improper access control due to a missing permission check allowing other authenticated users to create mail aliases for other users.

## References
- https://github.com/nextcloud/mail/pull/4864
- https://github.com/nextcloud/mail/releases/tag/v1.9.5
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-jmgp-77jq-fjp3
- https://hackerone.com/reports/1129996
- https://nvd.nist.gov/vuln/detail/CVE-2021-22896
