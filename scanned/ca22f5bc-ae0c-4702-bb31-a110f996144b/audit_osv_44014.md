# [M] JuiceFS Local Filestore Backend Joins Object Keys onto the Storage Root Without a Containment Check, Allowing Writes Outside the Configured Directory

## Summary
Severity: Medium
Advisory: CVE-2026-77763
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77763
Type: osv

## Details
The filestore backend in pkg/object/file.go, used for file:// stores and as a common juicefs sync destination, derived every operation's target from path(key), which returned either filepath.Join(d.root, key) or filepath.Clean(d.root + key) with no check that the result stayed beneath the root. Put, Get, Head, Delete, Chmod, Chown, Symlink and Readlink all consumed that value directly. Object keys enumerated from a source object store during a sync are not constrained the way local filesystem names are, so a key containing traversal segments causes juicefs to write attacker-supplied content to a path outside the intended local destination, and no error is returned. An operator syncing from a bucket whose contents they do not fully control, such as a shared or public bucket or one an attacker can write to, is therefore exposed to a file write at an attacker-influenced location. The fix changes path() to return an error and rejects any key whose resolved path escapes the root.

## References
- https://proxy.golang.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77763.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77763
- https://www.vulncheck.com/advisories/juicefs-local-filestore-backend-joins-object-keys-onto-the-storage-root-without-a-containment-check-allowing-writes-outside-the-configured-directory
- https://github.com/juicedata/juicefs/issues/7401
- https://github.com/juicedata/juicefs/pull/7425
- https://github.com/juicedata/juicefs/commit/0bcd70b3d13088d38127d6fb5750c91be7c4ec16
- https://github.com/juicedata/juicefs
- https://github.com/juicedata/juicefs/blob/v1.4.1/pkg/object/file.go
