# [H] Vulnerability allowing for reading internal HTTP resources

## Summary
Severity: High
Advisory: GHSA-hfwx-c7q6-g54c
CWE: CWE-552
Ecosystem: npm
Published: 2021-03-12
Source: https://github.com/advisories/GHSA-hfwx-c7q6-g54c
Type: github-advisory

## Affected
- npm: `highcharts-export-server` — affected >=0 <2.1.0

## Details
### Impact

The vulnerability allows for reading and outputting files served by other services on the internal network in which the export server is hosted. If the export server is exposed to the internet, this potentially allows a malicious user to gain read access to internal web-resources.

The impact is limited to internal services that serve content via. HTTP(S), and requires the attacker to know internal hostnames/IP addresses.

The previous versions have been marked as deprecated on NPM.

### Patches

Version 2.1.0 released alongside this security advisory addresses the issue. **Please note that this release is not backwards compatible out of the box. See the [changelog](https://github.com/highcharts/node-export-server/blob/master/CHANGELOG.md) for details.**

Additionally, it's also recommended to upgrade to the latest version of Highcharts to get the added input sanitation implemented in version 9.0 and later. 

### Workarounds

There are no known workarounds to the issue - an upgrade to version 2.1.0 is required.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the export server issue tracker](https://github.com/highcharts/node-export-server/issues)
* Email us at [security@highsoft.com](mailto:security@highsoft.com)

## References
- https://github.com/highcharts/node-export-server/security/advisories/GHSA-hfwx-c7q6-g54c
- https://github.com/highcharts/node-export-server/commit/53fa992a96785a5a08390e55ec30ea2ad217dfe6
- https://github.com/highcharts/node-export-server/blob/master/CHANGELOG.md#210
- https://www.npmjs.com/package/highcharts-export-server
