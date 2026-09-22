# [M] CVE-2016-10534

## Summary
Severity: Medium
Advisory: CVE-2016-10534
Aliases: GHSA-q43m-ffwr-rpcc
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-05-31
Source: https://osv.dev/vulnerability/CVE-2016-10534
Type: osv

## Details
electron-packager is a command line tool that packages Electron source code into `.app` and `.exe` packages. along with Electron. The `--strict-ssl` command line option in electron-packager >= 5.2.1 <= 6.0.0 || >=6.0.0 <= 6.0.2 defaults to false if not explicitly set to true. This could allow an attacker to perform a man in the middle attack.

## References
- https://nodesecurity.io/advisories/104
- https://github.com/electron-userland/electron-packager/issues/333
