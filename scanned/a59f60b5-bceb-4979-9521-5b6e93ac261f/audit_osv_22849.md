# [H] Metabase vulnerable to arbitrary SQL execution from queryhash

## Summary
Severity: High
Advisory: CVE-2022-39362
Aliases: GHSA-93wj-fgjg-r238
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-26
Source: https://osv.dev/vulnerability/CVE-2022-39362
Type: osv

## Details
Metabase is data visualization software. Prior to versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, 1.42.6, 0.41.9, and 1.41.9, unsaved SQL queries are auto-executed, which could pose a possible attack vector. This issue is patched in versions 0.44.5, 1.44.5, 0.43.7, 1.43.7, 0.42.6, 1.42.6, 0.41.9, and 1.41.9. Metabase no longer automatically executes ad-hoc native queries. Now the native editor shows the query and gives the user the option to manually run the query if they want.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39362.json
- https://github.com/metabase/metabase/security/advisories/GHSA-93wj-fgjg-r238
- https://nvd.nist.gov/vuln/detail/CVE-2022-39362
- https://github.com/metabase/metabase/commit/b7c6bb905a9187347cfc9035443b514713027a5c
