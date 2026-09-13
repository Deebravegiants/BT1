# [M] Backups directory .htaccess deletion in. MyBB

## Summary
Severity: Medium
Advisory: CVE-2024-23335
Aliases: GHSA-94xr-g4ww-j47r
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-23335
Type: osv

## Details
MyBB is a free and open source forum software. The backup management module of the Admin CP may accept `.htaccess` as the name of the backup file to be deleted, which may expose the stored backup files over HTTP on Apache servers. MyBB 1.8.38 resolves this issue. Users are advised to upgrade. There are no known workarounds for this vulnerability

## References
- https://mybb.com/versions/1.8.38
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23335.json
- https://github.com/mybb/mybb/security/advisories/GHSA-94xr-g4ww-j47r
- https://nvd.nist.gov/vuln/detail/CVE-2024-23335
- https://github.com/mybb/mybb/commit/450259e501b94c9d483efb167cb2bf875605e111.patch
