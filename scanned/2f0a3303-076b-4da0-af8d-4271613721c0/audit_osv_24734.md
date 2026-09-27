# [M] rootless: `/sys/fs/cgroup` is writable when cgroupns isn't unshared in runc

## Summary
Severity: Medium
Advisory: CVE-2023-25809
Aliases: GHSA-m8cg-xc2p-r3fc, GO-2023-1682
CVSS: 5.0 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2023-03-29
Source: https://osv.dev/vulnerability/CVE-2023-25809
Type: osv

## Details
runc is a CLI tool for spawning and running containers according to the OCI specification. In affected versions it was found that rootless runc makes `/sys/fs/cgroup` writable in following conditons: 1. when runc is executed inside the user namespace, and the `config.json` does not specify the cgroup namespace to be unshared (e.g.., `(docker|podman|nerdctl) run --cgroupns=host`, with Rootless Docker/Podman/nerdctl) or 2. when runc is executed outside the user namespace, and `/sys` is mounted with `rbind, ro` (e.g., `runc spec --rootless`; this condition is very rare). A container may gain the write access to user-owned cgroup hierarchy `/sys/fs/cgroup/user.slice/...` on the host . Other users's cgroup hierarchies are not affected. Users are advised to upgrade to version 1.1.5. Users unable to upgrade may unshare the cgroup namespace (`(docker|podman|nerdctl) run --cgroupns=private)`. This is the default behavior of Docker/Podman/nerdctl on cgroup v2 hosts. or add `/sys/fs/cgroup` to `maskedPaths`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25809.json
- https://github.com/opencontainers/runc/security/advisories/GHSA-m8cg-xc2p-r3fc
- https://nvd.nist.gov/vuln/detail/CVE-2023-25809
- https://github.com/opencontainers/runc/commit/0d62b950e60f6980b54fe3bafd9a9c608dc1df17
