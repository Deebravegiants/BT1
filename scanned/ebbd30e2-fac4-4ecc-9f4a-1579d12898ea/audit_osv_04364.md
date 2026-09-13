# [M] BIT-discourse-2022-39232

## Summary
Severity: Medium
Advisory: BIT-discourse-2022-39232
Aliases: CVE-2022-39232, GHSA-cv64-v73f-7wq5
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-discourse-2022-39232
Type: osv

## Affected
- Bitnami: `discourse` — affected >=2.9.0-beta9

## Details
Discourse is an open source discussion platform. Starting with version 2.9.0.beta5 and prior to version 2.9.0.beta10, an incomplete quote can generate a JavaScript error which will crash the current page in the browser in some cases. Version 2.9.0.beta10 added a fix and tests to ensure incomplete quotes won't break the app. As a workaround, the quote can be fixed via the rails console.

## References
- https://github.com/discourse/discourse/commit/eab33af5bf19827527fe79134d865b5c727f6530
- https://github.com/discourse/discourse/pull/18311
- https://github.com/discourse/discourse/security/advisories/GHSA-cv64-v73f-7wq5
