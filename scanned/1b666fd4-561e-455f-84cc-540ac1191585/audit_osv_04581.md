# [H] Discourse: Strip SQL comments and use non-recursive parameter interpolation in Data Explorer

## Summary
Severity: High
Advisory: BIT-discourse-2026-72731
Aliases: CVE-2026-72731, GHSA-wm63-83xp-59r5
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-discourse-2026-72731
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2026.7.0 <2026.7.1

## Details
Discourse is an open-source discussion platform. From 2026.1.0 until 2026.1.7, 2026.6.2, 2026.7.1, and 2026.8.0, anyone able to run a parameterized Data Explorer query, including non-staff members of a group a query is shared with, could craft parameter values that escaped the intended query and executed arbitrary SQL through plugins/discourse-data-explorer/lib/discourse_data_explorer/data_explorer.rb and plugins/discourse-data-explorer/lib/discourse_data_explorer/workflows/sql_action/v1.rb. Recursive parameter interpolation allowed one parameter value to introduce another parameter, and parameter declarations in SQL comments could be used to inject a statement. Queries run in a read-only transaction, so data could not be modified, but any table could be read. This issue is fixed in versions 2026.1.7, 2026.6.2, 2026.7.1, and 2026.8.0.

## References
- https://github.com/discourse/discourse/commit/2bdab888cef561348470dee204a4879d83fbb5c3
- https://github.com/discourse/discourse/commit/3dc7f0da7aa18548281152e285244efb1cc8ad0d
- https://github.com/discourse/discourse/commit/674ba6fc64184fd7d8e21183c5d8cb22367faa6e
- https://github.com/discourse/discourse/commit/ce9ccf24ec3538172dc8f8199728e08f63e57693
- https://github.com/discourse/discourse/security/advisories/GHSA-wm63-83xp-59r5
- https://nvd.nist.gov/vuln/detail/CVE-2026-72731
