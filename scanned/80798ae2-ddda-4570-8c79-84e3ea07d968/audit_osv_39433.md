# [H] Nextcloud: Tables app allows limited SQLi in ORDER BY with malicious sort order argument for Table Views

## Summary
Severity: High
Advisory: CVE-2026-45722
Aliases: GHSA-5h2w-c7px-hp4j
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45722
Type: osv

## Details
Nextcloud is an open source content collaboration platform. From versions 0.9.0 to before 0.9.7, and 1.0.0 to before 1.0.2, a missing sanitization in the Tables app allowed a user with access to the tables app to perform a limited SQL injection in the ORDER BY statement of a query. Compared to normal SQL injections, the ORDER BY is limited to extracting a single bit of information per request or to make the database wait for a given time. This issue has been patched in versions 0.9.7 and 1.0.2.

## References
- https://hackerone.com/reports/3446689
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45722.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-5h2w-c7px-hp4j
- https://nvd.nist.gov/vuln/detail/CVE-2026-45722
- https://github.com/nextcloud/tables/pull/2186
