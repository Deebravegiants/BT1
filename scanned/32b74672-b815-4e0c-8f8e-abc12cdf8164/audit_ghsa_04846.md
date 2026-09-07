# [M] Daytona: Path traversal in sandbox volume id mounts arbitrary host paths into the sandbox — cross-tenant data access and host escape

## Summary
Severity: Medium
Advisory: GHSA-fjv8-j4p5-cr9m
CVE: CVE-2026-54319
CWE: CWE-20, CWE-22, CWE-250, CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-fjv8-j4p5-cr9m
Type: github-advisory

## Affected
- Go: `github.com/daytonaio/daytona` — affected >=0 <0.186.0

## Details
## Summary
A sandbox volume reference (`volumeId`, which may also be a volume name) was forwarded to the
runner and used to build the host bind-mount source path without confinement. A reference
containing path-traversal sequences could in principle resolve the mount source outside the
intended per-volume base directory.

## Impact
Had the traversal been reachable, an authenticated user could have caused the runner to
bind-mount an unintended host path into their sandbox, with a worst-case impact of read and
write access to other tenants' volume data (per-volume FUSE mounts are world-readable and
writable).

Important: this path was not exploitable in any released version. A volume reference is
validated against the database before it reaches the runner, and the volume id column is a
UUID type, so a reference containing traversal sequences is rejected at validation time and
the request fails before any mount is constructed. We could not reproduce cross-tenant access
or an out-of-base host mount on a released build; the observable effect of the documented
payload was a server-side validation error. Severity is assessed as Medium on that basis.

## Patches
Fixed in v0.186.0. Volume references are now resolved to the canonical volume UUID
server-side before reaching the runner, so a name can never flow downstream as a path
component, and the runner confines the mount source to the volume base directory and rejects
any non-UUID reference.

## Workarounds
Upgrade to v0.186.0 or later. No configuration workaround is required for released versions,
which were not exploitable.

## Credit
Reported by @vnth4nhnt from CyStack.

## References
- https://github.com/daytonaio/daytona/security/advisories/GHSA-fjv8-j4p5-cr9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-54319
- https://github.com/daytonaio/daytona
