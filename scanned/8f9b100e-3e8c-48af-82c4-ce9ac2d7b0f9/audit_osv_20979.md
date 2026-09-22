# [H] CVE-2021-39225

## Summary
Severity: High
Advisory: CVE-2021-39225
Aliases: GHSA-2x96-38qg-3m72
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-39225
Type: osv

## Details
Nextcloud is an open-source, self-hosted productivity platform. A missing permission check in Nextcloud Deck before 1.2.9, 1.4.5 and 1.5.3 allows another authenticated users to access Deck cards of another user. It is recommended that the Nextcloud Deck App is upgraded to 1.2.9, 1.4.5 or 1.5.3. There are no known workarounds aside from upgrading.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-2x96-38qg-3m72
- https://hackerone.com/reports/1331728
- https://github.com/nextcloud/deck/pull/3316
