# [H] Kata guest escape: runtime-rs guest-root to host-root escape via virtiofs

## Summary
Severity: High
Advisory: GHSA-2gv2-cffp-j227
CVE: CVE-2026-47243
CWE: CWE-22, CWE-36
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:H/SI:H/SA:N/E:P (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-2gv2-cffp-j227
Type: github-advisory

## Affected
- Go: `github.com/kata-containers/kata-containers` — affected >=0 <0.0.0-20260519062212-ffa59ce3aa78

## Details
### Summary

In the runtime-rs standalone virtio-fs path, verified here with QEMU (and verified with Cloud Hypervisor too), Kata Containers runs host `virtiofsd` as root with:

```
--sandbox none --seccomp none
```

If an attacker has root-equivalent execution inside the Kata guest VM, they can send raw FUSE requests directly to the host `virtiofsd`. With the tested runtime-rs virtio-fs configuration, a raw `FUSE_SYMLINK` request whose new symlink name is an absolute host path is honored outside the virtio-fs shared directory.

This lets guest root create host-root owned symlinks in sensitive host paths. The PoC created here will create symlinks in the host `/etc/cron.d` directory, causing host cron to execute a guest-controlled payload as host root.

Impact: guest root can execute code as host root.

### Affected configuration

The verified host used:

```
/opt/kata/share/defaults/kata-containers/runtime-rs/configuration-qemu-runtime-rs.toml

rootless = false
shared_fs = "virtio-fs"
virtio_fs_daemon = "/opt/kata/libexec/virtiofsd"
hypervisor_name = "qemu"
debug_console_enabled = false
```

Pinned upstream references, using Kata Containers `main` commit `2ffd1538a296cff93a357bfba0dfca747480a1f8`:

- runtime-rs standalone virtio-fs adds [`--sandbox none --seccomp none`](https://github.com/kata-containers/kata-containers/blob/2ffd1538a296cff93a357bfba0dfca747480a1f8/src/runtime-rs/crates/resource/src/share_fs/share_virtio_fs_standalone.rs#L82-L92) to the `virtiofsd` command line.
- runtime-rs QEMU leaves rootless mode disabled by default: [`rootless = false`](https://github.com/kata-containers/kata-containers/blob/2ffd1538a296cff93a357bfba0dfca747480a1f8/src/runtime-rs/config/configuration-qemu-runtime-rs.toml.in#L31-L34).
- The QEMU runtime-rs config template generates an installed config that uses standalone virtio-fs and points runtime-rs at the host `virtiofsd` binary: [`shared_fs` and `virtio_fs_daemon`](https://github.com/kata-containers/kata-containers/blob/2ffd1538a296cff93a357bfba0dfca747480a1f8/src/runtime-rs/config/configuration-qemu-runtime-rs.toml.in#L164-L171).
- The runtime-rs Makefile resolves those placeholders to [`virtio-fs`](https://github.com/kata-containers/kata-containers/blob/2ffd1538a296cff93a357bfba0dfca747480a1f8/src/runtime-rs/Makefile#L496-L499) and [`$(LIBEXECDIR)/virtiofsd`](https://github.com/kata-containers/kata-containers/blob/2ffd1538a296cff93a357bfba0dfca747480a1f8/src/runtime-rs/Makefile#L184-L190).
- runtime-rs selects the same standalone virtio-fs implementation whenever `shared_fs = "virtio-fs"`: [`ShareVirtioFsStandalone`](https://github.com/kata-containers/kata-containers/blob/2ffd1538a296cff93a357bfba0dfca747480a1f8/src/runtime-rs/crates/resource/src/share_fs/mod.rs#L158-L167).

### Details

The guest kernel normally owns the virtio-fs client. A normal guest process will use filesystem syscalls, and the guest kernel will validate the paths, and only then does the kernel send FUSE messages to the host backend.

An attacker with root-equivalent access inside the guest can bypass that guest virtio-fs client. They can access the virtio-fs PCI device, mmap the virtio PCI BAR, recover guest physical addresses from `/proc/self/pagemap`, and build their own virtqueue from userspace. That queue can submit attacker-built FUSE messages directly to host `virtiofsd`.

The relevant primitive is `FUSE_SYMLINK`. An attacker can send a request whose body contains:

```
new symlink name: /etc/cron.d/kata-go-escape-cron-<pid>
symlink target: /proc/<pid>/root/run/kata-containers/shared/sandboxes/<sid>/ro/passthrough/<sid>/rootfs/tmp/kata-go-escape-payload
```

The new symlink name is an absolute host path. `virtiofsd` should reject that request or force it to resolve below the configured `--shared-dir`. In the tested runtime-rs path, host-root unsandboxed `virtiofsd` accepts the absolute name, creating a real host symlink under `/etc/cron.d`.

The attacker can make the symlink target resolve through `/proc/<pid>/root/...` for a live Kata runtime process whose mount namespace can see the guest-created payload. One matching runtime PID is enough.

When the host cron reads `/etc/cron.d`, it follows the root-owned symlink, loads the guest-created crontab payload, and executes it as host root.

### PoC

```shell
sudo timeout --foreground --kill-after=10s 600s ctr run --rm \
  --runtime /opt/kata/runtime-rs/bin/containerd-shim-kata-v2 \
  --runtime-config-path /opt/kata/share/defaults/kata-containers/runtime-rs/configuration-qemu-runtime-rs.toml \
  --privileged \
  --privileged-without-host-devices \
  docker.io/library/kata-go-escape:local \
  "$run_id"
```

The container is privileged only to model the post-escape condition where the attacker already has guest-root capabilities. It is not the vulnerability by itself.

Inside the guest, the PoC:

1. Writes a cron payload to guest `/tmp/kata-go-escape-payload`.
2. Finds the virtio-fs PCI device in guest /sys.
3. Takes over a virtio-fs queue from userspace.
4. Sends `FUSE_INIT`.
5. Discovers the current runtime-rs sandbox under `passthrough/`.
6. Looks up `passthrough/<sid>/rootfs/tmp/kata-go-escape-payload`.
7. Sends raw `FUSE_SYMLINK` requests where the new symlink names are absolute host paths under `/etc/cron.d`.
8. Keeps the guest alive while host cron scans.

Example log lines:

```
[guest] virtio-fs PCI device: /sys/devices/pci0000:00/0000:00:05.0
[res] sandbox_id=kata-go-escape-test-1778522686-1539
[res] lookup_path_error=0 path=passthrough/kata-go-escape-test-1778522686-1539/rootfs/tmp/kata-go-escape-payload nodeid=21
[spray] pid=1 err=-2 created_candidates=1
```

`err=-2` is expected for the symlink spray. `virtiofsd` can return `ENOENT` after the side effect because its follow-up lookup is still relative to the export root. The host symlink creation has already happened.

### Impact

The PoC proves guest-root to host-root command execution.

Verified host proof:

```
/run/kata-go-escape.proof

uid=0(root) gid=0(root) groups=0(root)
Mon May 11 18:05:01 UTC 2026
```

The proof file is written in host `/run` by host cron. It is not written by the guest process and not written by `virtiofsd`.

An attacker who reaches guest root can therefore cross the Kata isolation boundary and execute commands as host root on affected runtime-rs virtio-fs deployments.

## References
- https://github.com/kata-containers/kata-containers/security/advisories/GHSA-2gv2-cffp-j227
- https://github.com/kata-containers/kata-containers/commit/ffa59ce3aa7877d067c9a372df0c329a23a01744
- https://github.com/kata-containers/kata-containers
- https://github.com/kata-containers/kata-containers/releases/tag/3.31.0
