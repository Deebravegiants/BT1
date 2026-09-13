# [H] H2O vulnerable to read from uninitialized pointer in the reverse proxy handler

## Summary
Severity: High
Advisory: CVE-2023-30847
Aliases: GHSA-p5hj-phwj-hrvx
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2023-04-27
Source: https://osv.dev/vulnerability/CVE-2023-30847
Type: osv

## Details
H2O is an HTTP server. In versions 2.3.0-beta2 and prior, when the reverse proxy handler tries to processes a certain type of invalid HTTP request, it tries to build an upstream URL by reading from uninitialized pointer. This behavior can lead to crashes or leak of information to back end HTTP servers. Pull request  number 3229 fixes the issue. The pull request has been merged to the `master` branch in commit f010336. Users should upgrade to commit f010336 or later.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30847.json
- https://github.com/h2o/h2o/security/advisories/GHSA-p5hj-phwj-hrvx
- https://nvd.nist.gov/vuln/detail/CVE-2023-30847
- https://github.com/h2o/h2o/commit/f010336bab162839df43d9e87570897466c97e33
- https://github.com/h2o/h2o/pull/3229
