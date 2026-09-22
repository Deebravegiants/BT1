# [H] CVE-2021-37628

## Summary
Severity: High
Advisory: CVE-2021-37628
Aliases: GHSA-pxhh-954f-8w7w
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-37628
Type: osv

## Details
Nextcloud Richdocuments is an open source collaborative office suite. In affected versions the File Drop features ("Upload Only" public link shares in Nextcloud) can be bypassed using the Nextcloud Richdocuments app. An attacker was able to read arbitrary files in such a share. It is recommended that the Nextcloud Richdocuments is upgraded to 3.8.4 or 4.2.1. If upgrading is not possible then it is recommended to disable the Richdocuments application.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-pxhh-954f-8w7w
- https://hackerone.com/reports/1253403
- https://github.com/nextcloud/richdocuments/pull/1664
