# [H] Incorrect Authorization in Bareos Director

## Summary
Severity: High
Advisory: CVE-2022-24755
Aliases: GHSA-4979-8ffj-4q26
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-15
Source: https://osv.dev/vulnerability/CVE-2022-24755
Type: osv

## Details
Bareos is open source software for backup, archiving, and recovery of data for operating systems. When Bareos Director >= 18.2 >= 18.2 but prior to 21.1.0, 20.0.6, and 19.2.12 is built and configured for PAM authentication, it will skip authorization checks completely. Expired accounts and accounts with expired passwords can still login. This problem will affect users that have PAM enabled. Currently there is no authorization (e.g. check for expired or disabled accounts), but only plain authentication (i.e. check if username and password match). Bareos Director versions 21.1.0, 20.0.6 and 19.2.12 implement the authorization check that was previously missing. The only workaround is to make sure that authentication fails if the user is not authorized.

## References
- https://huntr.dev/bounties/480121f2-bc3c-427e-986e-5acffb1606c5/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24755.json
- https://github.com/bareos/bareos/security/advisories/GHSA-4979-8ffj-4q26
- https://nvd.nist.gov/vuln/detail/CVE-2022-24755
- https://github.com/bareos/bareos/pull/1115
- https://github.com/bareos/bareos/pull/1119
- https://github.com/bareos/bareos/pull/1121
