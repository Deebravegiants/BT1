# [M] Singluarity: Incorrect path matching for 'limit container paths' directive

## Summary
Severity: Medium
Advisory: GHSA-wqcr-7rf3-f64m
CVE: CVE-2026-47215
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-wqcr-7rf3-f64m
Type: github-advisory

## Affected
- Go: `github.com/sylabs/singularity/v4` — affected >=0 <4.4.2
- Go: `github.com/sylabs/singularity` — affected >=0

## Details
### Impact

The `limit container paths` directive in `singularity.conf` is intended to allow a system administrator limit the paths from which containers can be run, under setuid mode. Due to incorrect matching of a path string, sibling directories with similar names may incorrectly be allowed.

For example, the configuration:

```
limit container paths = /data/safe
```

Will also allow containers in `/data/safe-but-unsafe` to be run.


### Patches

This issue is patched in SingularityCE 4.4.2 and SingularityPRO 4.3.9 / 4.1.14

### Workarounds

If you do not use the `limit container paths` functionality, then this issue does not affect your installation.

If you do use the `limit container paths` functionality then you must update. Please also review the documented limitations when user namespaces are enabled [1].

## References
- https://github.com/sylabs/singularity/security/advisories/GHSA-wqcr-7rf3-f64m
- https://github.com/sylabs/singularity/commit/c08791793e843d4c9c1f2fc1d9d12abef747378f
- https://docs.sylabs.io/guides/latest/admin-guide/configfiles.html#limiting-container-execution
- https://github.com/sylabs/singularity
- https://github.com/sylabs/singularity/releases/tag/v4.4.2
