# [C] Gogs allows argument injection during the previewing of changes

## Summary
Severity: Critical
Advisory: GHSA-9pp6-wq8c-3w2c
CVE: CVE-2024-39932
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.1/AC:L/AV:N/A:H/C:H/I:H/PR:L/S:C/UI:N (CVSS_V3)
Published: 2024-12-23
Source: https://github.com/advisories/GHSA-9pp6-wq8c-3w2c
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.1

## Details
### Impact

Unprivileged user accounts can write to arbitrary files on the filesystem. We could demonstrate its exploitation to force a re-installation of the instance, granting administrator rights. It allows accessing and altering any user's code hosted on the same instance.

### Patches

Unintended Git options has been ignored for diff preview (https://github.com/gogs/gogs/pull/7871). Users should upgrade to 0.13.1 or the latest 0.14.0+dev.

### Workarounds

No viable workaround available, please only grant access to trusted users to your Gogs instance on affected versions.

### References

https://www.cve.org/CVERecord?id=CVE-2024-39932

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-9pp6-wq8c-3w2c
- https://nvd.nist.gov/vuln/detail/CVE-2024-39932
- https://github.com/gogs/gogs
- https://www.sonarsource.com/blog/securing-developer-tools-unpatched-code-vulnerabilities-in-gogs-1
