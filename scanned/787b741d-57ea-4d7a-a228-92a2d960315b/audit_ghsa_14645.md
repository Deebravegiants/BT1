# [C] Gogs allows deletion of internal files

## Summary
Severity: Critical
Advisory: GHSA-ccqv-43vm-4f3w
CVE: CVE-2024-39931
CWE: CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AC:L/AV:N/A:H/C:H/I:H/PR:L/S:C/UI:N (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-ccqv-43vm-4f3w
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.1

## Details
### Impact

Unprivileged user accounts can execute arbitrary commands on the Gogs instance with the privileges of the account specified by `RUN_USER` in the configuration. It allows attackers to access and alter any users' code hosted on the same instance.

### Patches

Deletion of `.git` files has been prohibited (https://github.com/gogs/gogs/pull/7870). Users should upgrade to 0.13.1 or the latest 0.14.0+dev.

### Workarounds

No viable workaround available, please only grant access to trusted users to your Gogs instance on affected versions.

### References

https://www.cve.org/CVERecord?id=CVE-2024-39931

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-ccqv-43vm-4f3w
- https://nvd.nist.gov/vuln/detail/CVE-2024-39931
- https://github.com/gogs/gogs
- https://www.sonarsource.com/blog/securing-developer-tools-unpatched-code-vulnerabilities-in-gogs-1
