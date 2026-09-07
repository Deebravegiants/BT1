# [M] K3s: ZIP Archive Path Traversal Vulnerability in etcd Snapshot Decompression

## Summary
Severity: Medium
Advisory: GHSA-jxr7-mqhw-9p98
CVE: CVE-2026-54250
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-jxr7-mqhw-9p98
Type: github-advisory

## Affected
- Go: `github.com/k3s-io/k3s` — affected >=1.35.0-rc1 <1.35.3
- Go: `github.com/k3s-io/k3s` — affected >=1.34.0-rc1 <1.34.6
- Go: `github.com/k3s-io/k3s` — affected >=0 <1.33.10

## Details
#### Summary

A path traversal vulnerability exists in K3s's etcd snapshot decompression functionality. Zip files containing archive members with maliciously crafted names (e.g., `../../../../etc/password`) can be written to arbitrary locations on the filesystem when an administrator restores the archive as a compressed etcd snapshot.

#### Mitigations

* Enable golang's built-in [insecure path protections](https://pkg.go.dev/archive/zip#NewReader) when restoring snapshots by setting the`GODEBUG` environment variable:
    ```bash
    GODEBUG=zipinsecurepath=0 k3s server --cluster-reset --cluster-reset-restore-path=/path/to/snapshot.zip
    ```
* Manually extract the snapshot from the zip archive before restoring it. If the snapshot to be restored does not end with `.zip`, the vulnerable extraction code will not be executed.

#### Additional Notes

Administrators should be aware of the cautions noted in the "Security" section of the documentation on [Restoring Snapshots](https://docs.k3s.io/cli/etcd-snapshot#security).

## References
- https://github.com/k3s-io/k3s/security/advisories/GHSA-jxr7-mqhw-9p98
- https://nvd.nist.gov/vuln/detail/CVE-2026-54250
- https://github.com/k3s-io/k3s
