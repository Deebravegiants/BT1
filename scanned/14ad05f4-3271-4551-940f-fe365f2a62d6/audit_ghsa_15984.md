# [M] Extract has insufficient checks allowing attacker to create symlinks outside the extraction directory.

## Summary
Severity: Medium
Advisory: GHSA-8rm2-93mq-jqhc
CVE: CVE-2024-47877
CWE: CWE-22, CWE-61
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-10-11
Source: https://github.com/advisories/GHSA-8rm2-93mq-jqhc
Type: github-advisory

## Affected
- Go: `github.com/codeclysm/extract/v3` — affected >=0
- Go: `github.com/codeclysm/extract/v4` — affected >=0 <4.0.0
- Go: `github.com/codeclysm/extract` — affected >=0

## Details
### Impact
A maliciously crafted archive may allow an attacker to create a symlink outside the extraction target directory.

### Patches
Please use version 4.0.0 or later `github.com/codeclysm/extract/v4`. Any previous version is affected by the bug.

### Workarounds
No knows workarounds.

### Backward compatibility notes about upgrading to `/v4` from `/v3`

If you're not using the `extract.Extractor.FS` interface, you will not face any breaking changes and upgrading should be as simple as changing the import to `/v4`. This should be the case for most of the userbase.

If you're using the `Extractor.FS` interface, then upgrading to `/v4` will require to implement the new methods that have been added:

```go
type FS interface {
    Link(string, string) error
    MkdirAll(string, os.FileMode) error
    OpenFile(name string, flag int, perm os.FileMode) (*os.File, error)
    Symlink(string, string) error

    // The following methods have been added in the /v4 interface:

    Remove(path string) error
    Stat(name string) (os.FileInfo, error)
    Chmod(name string, mode os.FileMode) error
}
```

There should be no other breaking changes in the `/v4` API.

## References
- https://github.com/codeclysm/extract/security/advisories/GHSA-8rm2-93mq-jqhc
- https://nvd.nist.gov/vuln/detail/CVE-2024-47877
- https://github.com/codeclysm/extract/commit/4a98568021b8e289345c7f526ccbd7ed732cf286
- https://github.com/codeclysm/extract
