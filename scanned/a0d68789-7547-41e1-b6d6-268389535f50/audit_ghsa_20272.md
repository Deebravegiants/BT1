# [M] Cross-site Scripting vulnerability in repository issue list in Gogs

## Summary
Severity: Medium
Advisory: GHSA-xq4v-vrp9-vcf2
CVE: CVE-2022-31038
CWE: CWE-79, CWE-80
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-08
Source: https://github.com/advisories/GHSA-xq4v-vrp9-vcf2
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.12.9

## Details
### Impact
`DisplayName` allows all the characters from users, which leads to an XSS vulnerability when directly displayed in the issue list.

### Patches
`DisplayName` is sanitized before being displayed. Users should upgrade to 0.12.9 or the latest 0.13.0+dev.

### Workarounds
Check and update the existing users' display names that contain malicious characters.

### References
N/A

### For more information
If you have any questions or comments about this advisory, please post on https://github.com/gogs/gogs/pull/7009.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-xq4v-vrp9-vcf2
- https://nvd.nist.gov/vuln/detail/CVE-2022-31038
- https://github.com/gogs/gogs/pull/7009
- https://github.com/gogs/gogs/commit/155cae1de8916fc3fde78f350763034b7422caee
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.12.9
