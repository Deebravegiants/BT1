# [M] Enumerable upload file names in hedgedoc

## Summary
Severity: Medium
Advisory: CVE-2022-24837
Aliases: GHSA-q6vv-2q26-j7rx
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-04-11
Source: https://osv.dev/vulnerability/CVE-2022-24837
Type: osv

## Details
HedgeDoc is an open-source, web-based, self-hosted, collaborative markdown editor. Images uploaded with HedgeDoc version 1.9.1 and later have an enumerable filename after the upload, resulting in potential information leakage of uploaded documents. This is especially relevant for private notes and affects all upload backends, except Lutim and imgur. This issue is patched in version 1.9.3 by replacing the filename generation with UUIDv4. If you cannot upgrade to HedgeDoc 1.9.3, it is possible to block POST requests to `/uploadimage`, which will disable future uploads.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24837.json
- https://github.com/hedgedoc/hedgedoc/security/advisories/GHSA-q6vv-2q26-j7rx
- https://nvd.nist.gov/vuln/detail/CVE-2022-24837
- https://github.com/node-formidable/formidable/issues/808
- https://github.com/hedgedoc/hedgedoc/commit/9e2f9e21e904c4a319e84265da7ef03b0a8e343a
