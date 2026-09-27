# [M] DoS via malicious record IDs in WatermelonDB

## Summary
Severity: Medium
Advisory: GHSA-38f9-m297-6q9g
CVE: CVE-2020-4035
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2020-06-03
Source: https://github.com/advisories/GHSA-38f9-m297-6q9g
Type: github-advisory

## Affected
- npm: `@nozbe/watermelondb` — affected >=0 <0.15.1
- npm: `@nozbe/watermelondb` — affected >=0.16.0 <0.16.2

## Details
## Impact

Medium severity 5.9 https://www.first.org/cvss/calculator/3.0#CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:H

A maliciously crafted record ID can exploit a SQL Injection vulnerability in iOS adapter implementation and cause the app to delete all or selected records from the database, generally causing the app to become unusable.

This may happen in apps that don't validate IDs (valid IDs are `/^[a-zA-Z0-9_-.]+$/`) and use Watermelon Sync or low-level `database.adapter.destroyDeletedRecords` method.

The integrity risk is low due to the fact that maliciously deleted records won't synchronize, so logout-login will restore all data, although some local changes may be lost if the malicious deletion causes the sync process to fail to proceed to push stage.

No way to breach confidentiality with this vulnerability is known. Full exploitation of SQL Injection is mitigated, because it's not possible to nest an insert/update query inside a delete query in SQLite, and it's not possible to pass a semicolon-separated second query. There's also no known practicable way to breach confidentiality by selectively deleting records, because those records will not be synchronized.

It's theoretically possible that selective record deletion could cause an app to behave insecurely if lack of a record is used to make security decisions by the app. 

## Patches

Patched versions include:

- 0.15.1
- 0.16.2
- 0.16.1-fix
	- this is actually the same as 0.16.0, but with the patch applied - as 0.16.1 is causing issues for some users
- `924c7ae2a8d` commit id contains the patch

## Workarounds

1. Ensure that your backend service sanitizes record IDs sent in the `pull sync` endpoint, such that only IDs matching `/^[a-zA-Z0-9_-.]+$/` are returned. This could also be done in JavaScript `pullChanges` function passed to `synchronize()`
2. If you use `destroyDeletedRecords` directly, validate all IDs passed the same way

## For more information

If you have any questions about this advisory, contact @radex.

## References
- https://github.com/Nozbe/WatermelonDB/security/advisories/GHSA-38f9-m297-6q9g
- https://nvd.nist.gov/vuln/detail/CVE-2020-4035
- https://github.com/Nozbe/WatermelonDB/commit/924c7ae2a8d7d6459656751e5b9b1bf91a218025
