# [C] linux-cmdline is vulnerable to Prototype Pollution via the constructor

## Summary
Severity: Critical
Advisory: GHSA-2c29-wc65-4cx9
CVE: CVE-2020-7704
CWE: CWE-1321, CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2c29-wc65-4cx9
Type: github-advisory

## Affected
- npm: `linux-cmdline` — affected >=0 <1.0.1

## Details
The package linux-cmdline is a parser for Linux kernel command line arguments. Versions before 1.0.1 are vulnerable to Prototype Pollution via the constructor.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7704
- https://github.com/piranna/linux-cmdline/commit/53c61a88bc47eb25d71832205056beaab95cf677
- https://github.com/piranna/linux-cmdline
- https://snyk.io/vuln/SNYK-JS-LINUXCMDLINE-598674
