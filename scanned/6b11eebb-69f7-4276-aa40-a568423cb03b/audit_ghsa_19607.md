# [M] github.com/jaredallard/archives Has Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')

## Summary
Severity: Medium
Advisory: GHSA-j95m-rcjp-q69h
CVE: CVE-2025-64346
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-03-28
Source: https://github.com/advisories/GHSA-j95m-rcjp-q69h
Type: github-advisory

## Affected
- Go: `github.com/jaredallard/archives` — affected >=0 <1.0.1

## Details
### Impact

A malicious user could feed a specially crafted archive to this library causing RCE, modification of files or other bad things in the context of whatever user is running this library as, through the program that imports it.

The severity highly depends on the user's permissions and environment it is being ran in (e.g., non root, read only root container would likely have no impact vs running something as root on a production system).

The severity is also dependent on **arbitrary archives** being passed or not.

Based on the above, severity high was picked to be safe.

### Patches

Patched with the help of snyk and gosec in v1.0.1

### Workarounds

The only workaround is to manually validate archives before submitting them to this library, however that is not recommended vs upgrading to unaffected versions.

### References

https://security.snyk.io/research/zip-slip-vulnerability

## References
- https://github.com/jaredallard/archives/security/advisories/GHSA-j95m-rcjp-q69h
- https://nvd.nist.gov/vuln/detail/CVE-2025-64346
- https://github.com/jaredallard/archives/commit/3bddec7bd3f38afbe97ae61d1c8a8487e9ea4ef1
- https://github.com/jaredallard/archives
