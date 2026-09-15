# [H] Path traversal in Icinga Web 2

## Summary
Severity: High
Advisory: CVE-2022-24716
Aliases: GHSA-5p3f-rh28-8frw
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-08
Source: https://osv.dev/vulnerability/CVE-2022-24716
Type: osv

## Details
Icinga Web 2 is an open source monitoring web interface, framework and command-line interface. Unauthenticated users can leak the contents of files of the local system accessible to the web-server user, including `icingaweb2` configuration files with database credentials. This issue has been resolved in versions 2.9.6 and 2.10 of Icinga Web 2. Database credentials should be rotated.

## References
- http://packetstormsecurity.com/files/171774/Icinga-Web-2.10-Arbitrary-File-Disclosure.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24716.json
- https://github.com/Icinga/icingaweb2/security/advisories/GHSA-5p3f-rh28-8frw
- https://nvd.nist.gov/vuln/detail/CVE-2022-24716
- https://security.gentoo.org/glsa/202208-05
- https://github.com/Icinga/icingaweb2/commit/9931ed799650f5b8d5e1dc58ea3415a4cdc5773d
