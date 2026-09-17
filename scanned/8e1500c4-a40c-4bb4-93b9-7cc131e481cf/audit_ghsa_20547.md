# [M] Incorrect Default Permissions in log4js

## Summary
Severity: Medium
Advisory: GHSA-82v2-mx6x-wq7q
CVE: CVE-2022-21704
CWE: CWE-276
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-82v2-mx6x-wq7q
Type: github-advisory

## Affected
- npm: `log4js` — affected >=0 <6.4.0

## Details
### Impact
Default file permissions for log files created by the file, fileSync and dateFile appenders are world-readable (in unix). This could cause problems if log files contain sensitive information. This would affect any users that have not supplied their own permissions for the files via the mode parameter in the config.

### Patches
Fixed by:
* https://github.com/log4js-node/log4js-node/pull/1141
* https://github.com/log4js-node/streamroller/pull/87

Released to NPM in log4js@6.4.0

### Workarounds
Every version of log4js published allows passing the mode parameter to the configuration of file appenders, see the documentation for details.

### References

Thanks to [ranjit-git](https://www.huntr.dev/users/ranjit-git) for raising the issue, and to @lamweili for fixing the problem.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [logj4s-node](https://github.com/log4js-node/log4js-node)
* Ask a question in the [slack channel](https://join.slack.com/t/log4js-node/shared_invite/enQtODkzMDQ3MzExMDczLWUzZmY0MmI0YWI1ZjFhODY0YjI0YmU1N2U5ZTRkOTYyYzg3MjY5NWI4M2FjZThjYjdiOGM0NjU2NzBmYTJjOGI)
* Email us at [gareth.nomiddlename@gmail.com](mailto:gareth.nomiddlename@gmail.com)

## References
- https://github.com/log4js-node/log4js-node/security/advisories/GHSA-82v2-mx6x-wq7q
- https://nvd.nist.gov/vuln/detail/CVE-2022-21704
- https://github.com/log4js-node/log4js-node/pull/1141/commits/8042252861a1b65adb66931fdf702ead34fa9b76
- https://github.com/log4js-node/streamroller/pull/87
- https://github.com/log4js-node/log4js-node
- https://github.com/log4js-node/log4js-node/blob/v6.4.0/CHANGELOG.md#640
- https://lists.debian.org/debian-lts-announce/2022/12/msg00014.html
