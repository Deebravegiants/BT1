# [M] LF Edge eKuiper: Arbitrary File and Directory Deletion via Path Traversal in Plugin Installation Endpoint

## Summary
Severity: Medium
Advisory: GHSA-c23q-fw86-9h5x
Aliases: CVE-2025-58363
Ecosystem: Go
Published: 2026-09-09
Source: https://osv.dev/vulnerability/GHSA-c23q-fw86-9h5x
Type: osv

## Affected
- Go: `github.com/lf-edge/ekuiper/v2` — affected >=0 <2.4.1

## Details
### Summary
A path traversal vulnerability in eKuiper's administrative management endpoints allows privileged users or attackers with access to management APIs to delete arbitrary files or directories on the host system.

### Details
In `internal/plugin/native/manager.go`, the plugin installation endpoint (`POST /plugins/*`) constructs a temporary directory path by directly joining user-supplied resource names (`name`) without sufficient sanitization. Supplying path traversal sequences (such as `../../...`) causes the deferred cleanup operation (`os.RemoveAll`) to target arbitrary directories outside the intended plugin directory.

A related issue in configuration and rule lifecycle management where unvalidated rule identifiers could influence file deletion paths was also addressed by introducing unified identifier and file name validation.

### PoC
1. Target file deletion via plugin installation endpoint:
```http
POST /plugins/sources HTTP/1.1
Host: 127.0.0.1:9081
Content-Type: application/json

{
  "name": "../../../../../tmp/target.txt",
  "file": "http://example.com/plugin.zip",
  "shellParas": [],
  "functions": []
}
```
2. When the request finishes, `/tmp/target.txt` is removed by `os.RemoveAll`.

### Impact
An attacker with access to eKuiper management APIs can cause arbitrary file or directory deletion, potentially leading to denial of service or disruption of the host environment. This vulnerability provides a delete-only capability and does not permit arbitrary file creation, modification, or code execution.

### Remediation & Patches
- **Upgrade to eKuiper >= 2.4.1**: Input validation (`validate.ValidateID`) and file path validation (`path.VerifyFileName`) have been enforced across management endpoints.

### Workarounds
- Restrict network access to eKuiper management port (`9081`) via authentication, reverse proxies, and firewall rules.
- Run eKuiper with a dedicated non-root user account to limit file system deletion permissions.

### Credits
- @kosmosec
- @arpitjain099

## References
- https://github.com/lf-edge/ekuiper/security/advisories/GHSA-c23q-fw86-9h5x
- https://github.com/lf-edge/ekuiper
- https://github.com/lf-edge/ekuiper/releases/tag/v2.4.1
