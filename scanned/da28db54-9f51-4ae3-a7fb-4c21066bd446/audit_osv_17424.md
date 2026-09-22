# [C] CVE-2020-15152

## Summary
Severity: Critical
Advisory: CVE-2020-15152
Aliases: GHSA-jw37-5gqr-cf9j
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-08-17
Source: https://osv.dev/vulnerability/CVE-2020-15152
Type: osv

## Details
ftp-srv is an npm package which is a modern and extensible FTP server designed to be simple yet configurable. In ftp-srv before versions 2.19.6, 3.1.2, and 4.3.4 are vulnerable to Server-Side Request Forgery. The PORT command allows arbitrary IPs which can be used to cause the server to make a connection elsewhere. A possible workaround is blocking the PORT through the configuration. This issue is fixed in version2 2.19.6, 3.1.2, and 4.3.4. More information can be found on the linked advisory.

## References
- https://www.npmjs.com/package/ftp-srv
- https://github.com/autovance/ftp-srv/commit/e449e75219d918c400dec65b4b0759f60476abca
- https://github.com/autovance/ftp-srv/security/advisories/GHSA-jw37-5gqr-cf9j
