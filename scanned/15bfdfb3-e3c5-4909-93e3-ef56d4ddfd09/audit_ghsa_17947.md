# [M] XWiki PDF export jobs store sensitive cookies unencrypted in job statuses

## Summary
Severity: Medium
Advisory: GHSA-9m7c-m33f-3429
CVE: CVE-2025-58049
CWE: CWE-212, CWE-257
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-28
Source: https://github.com/advisories/GHSA-9m7c-m33f-3429
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-export-pdf-api` — affected >=14.4.2 <16.4.8
- Maven: `org.xwiki.platform:xwiki-platform-export-pdf-api` — affected >=16.5.0-rc-1 <16.10.7
- Maven: `org.xwiki.platform:xwiki-platform-export-pdf-api` — affected >=17.0.0-rc-1 <17.4.0-rc-1

## Details
### Impact

The PDF export uses a background job that runs on the server-side. Jobs like this have a status that is serialized in the permanent directory when the job is finished. The job status includes the job request. The PDF export job request is initialized, before the job starts, with some context information that is needed to replicate the HTTP request (used to trigger the export) in the background thread used to run the export job. This context information includes the cookies from the HTTP request that triggered the export. As a result, the user cookies (including the encrypted username and password) are stored in the permanent directory after the PDF export is finished. As the encryption key is stored in the same data directory (by default it is generated in ``data/configuration.properties``), this means that this job status contains the equivalent of the plain text password of the user who requested the PDF export.

XWiki shouldn't store passwords in plain text, and it shouldn't be possible to gain access to plain text passwords by gaining access to, e.g., a backup of the data directory.

### Patches

This vulnerability has been patched in XWiki 16.4.8, 16.10.7 and 17.4.0RC1.

### Workarounds

We're not aware of any workarounds except for upgrading.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-9m7c-m33f-3429
- https://nvd.nist.gov/vuln/detail/CVE-2025-58049
- https://github.com/xwiki/xwiki-platform/commit/60982ad0057b1701ed8297f28cad35d170686539
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23151
