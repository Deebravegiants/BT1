# [H] modern-async's `forEachSeries` and `forEachLimit` functions do not limit the number of requests

## Summary
Severity: High
Advisory: GHSA-3pcq-34w5-p4g2
CVE: CVE-2021-41167
CWE: CWE-400, CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-21
Source: https://github.com/advisories/GHSA-3pcq-34w5-p4g2
Type: github-advisory

## Affected
- npm: `modern-async` — affected >=0 <1.0.4

## Details
### Impact

This is a bug affecting two of the functions in this library: `forEachSeries` and `forEachLimit`. They should limit the concurrency of some actions but, in practice, they don't. Any code calling these functions will be written thinking they would limit the concurrency but they won't. This could lead to potential security issues in other projects.

### Patches

The problem has been patched in 1.0.4.

### Workarounds

There is no workaround aside from upgrading to 1.0.4.

## References
- https://github.com/nicolas-van/modern-async/security/advisories/GHSA-3pcq-34w5-p4g2
- https://nvd.nist.gov/vuln/detail/CVE-2021-41167
- https://github.com/nicolas-van/modern-async/issues/5
- https://github.com/nicolas-van/modern-async/commit/0010d28de1b15d51db3976080e26357fa7144436
- https://github.com/nicolas-van/modern-async
