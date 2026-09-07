# [H] Improper sanitization of delegated role names

## Summary
Severity: High
Advisory: GHSA-r56q-vv3c-6g9c
CVE: CVE-2021-41150
CWE: CWE-22
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-10-19
Source: https://github.com/advisories/GHSA-r56q-vv3c-6g9c
Type: github-advisory

## Affected
- crates.io: `tough` — affected >=0 <0.12.0

## Details
### Impact
The tough library, prior to 0.12.0, does not properly sanitize delegated role names when caching a repository, or when loading a repository from the filesystem. When the repository is cached or loaded, files ending with the .json extension could be overwritten with role metadata anywhere on the system.

AWS would like to thank https://github.com/jku for reporting this issue.

### Patches
A fix is available in version 0.12.0.

### Workarounds
No workarounds to this issue are known.

### References
https://github.com/theupdateframework/python-tuf/security/advisories/GHSA-wjw6-2cqr-j4qr

## References
- https://github.com/awslabs/tough/security/advisories/GHSA-r56q-vv3c-6g9c
- https://github.com/theupdateframework/python-tuf/security/advisories/GHSA-wjw6-2cqr-j4qr
- https://nvd.nist.gov/vuln/detail/CVE-2021-41150
- https://github.com/awslabs/tough/commit/1809b9bd1106d78a51fbea3071aa97a3530bac9a
- https://github.com/awslabs/tough
