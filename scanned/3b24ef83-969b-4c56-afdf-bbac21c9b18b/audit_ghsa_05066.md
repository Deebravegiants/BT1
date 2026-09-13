# [M] runc: Malicious image with /dev symlink can trigger limited host filesystem integrity violations 

## Summary
Severity: Medium
Advisory: GHSA-xjvp-4fhw-gc47
CVE: CVE-2026-41579
CWE: CWE-61
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-xjvp-4fhw-gc47
Type: github-advisory

## Affected
- Go: `github.com/opencontainers/runc` — affected >=0 <1.3.6
- Go: `github.com/opencontainers/runc` — affected >=1.4.0 <1.4.3
- Go: `github.com/opencontainers/runc` — affected >=1.5.0-rc.1 <1.5.0-rc.3

## Details
### Impact
When setting up the container rootfs, `setupPtmx` and `setupDevSymlinks` call `os.Remove` and `os.Symlink` with a `filepath.Join` string which allow an image with `/dev` as a symlink to trick runc into deleting files called `ptmx` on the host or creating a hardcoded set of symlinks with specific names and targets in an arbitrary pre-existing host directory.

Please note that this issue is not exploitable under Docker because [it creates a top-level `ro` layer that masks any malicious `/dev` symlink present in the container image](https://github.com/moby/moby/blob/docker-v29.4.1/daemon/initlayer/setup_unix.go) (this is also done without mounting the lower layers so there is no opportunity for the malicious `/dev` symlink to trick it into resolving to some other path). Unfortunately, Podman and containerd<sup>&dagger;</sup> do not do this and so users using those higher-level runtimes with runc can be exploited via a malicious image.

This issue mirrors a [somewhat similar issue in crun](https://github.com/containers/crun/security/advisories/GHSA-7vwr-4279-7gq5), which was also published recently.

###### &dagger; Actually, at the time the issue was analysed, [containerd had dead code that implemented this feature](https://github.com/containerd/containerd/blob/v2.2.3/pkg/rootfs/init_linux.go) but the implementation contained several security issues that would arguably have made it more exploitable than in runc. Luckily, the code appears to have never been used (at least since 2017) and [the code has since been removed](https://github.com/containerd/containerd/issues/13238).

#### Mitigating Factors ####

There are a few mitigating factors about this issue which reduce the impact for most users quite significantly, and is the reason why we decided to release the fix publicly without an embargo.

While the deletion of `ptmx` seems like a significant issue, in practice it is quite limited. Notably, `devpts` does not permit you to unlink `/dev/pts/ptmx` regardless of privileges and so it is not a usable target for this attack. Additionally, while `/dev/ptmx` *can* be unlinked<sup>&ddagger;</sup>, trying to use an image with a symlink from `/dev` to `/dev` will cause runc will return an error before it reaches the buggy code (it correctly detects a symlink loop while setting up the mount target and the code correctly scopes the lookup inside the container). Thus, the only files called `ptmx` that are *guaranteed* to exist on the system cannot actually be removed by this bug and so only some user file that happens to have that specific name could be deleted, which seems fairly unlikely to happen on real systems.

As for the issue of symlinks, again the impact is likely quite limited. While the creation of *arbitrary* symlinks could be used to create drop-in files for system services (and thus lead to a container breakout), the hardcoded set of symlink names and targets that this bug allows you to create on the host make it quite unlikely that you would be able to do much more than pollute the host system with dummy symlinks. Here is the complete list of symlinks that can be created with this attack:

 * `core` &rarr; `/proc/kcore`
 * `fd` &rarr; `/proc/self/fd/`
 * `ptmx` &rarr; `pts/ptmx`
 * `stdin` &rarr; `/proc/self/fd/0`
 * `stdout` &rarr; `/proc/self/fd/1`
 * `stderr` &rarr; `/proc/self/fd/2`

Note that none of these symlinks are likely to point to user-controlled data -- the `/proc/self/fd/$n` symlinks are all properties of the process accessing them (so privileged processes will only see the state they were spawned with) and the `pts/ptmx` symlink is almost certainly in the same privilege scope as the directory the symlink itself is in. It seems the only somewhat plausible impact would be that a service could return an error when trying to parse one of these symlinks and thus treat it as an invalid configuration file. How arbitrary processes deal with this situation is a bit hard to analyse, but most daemons require configuration files to have certain suffixes (such as `.conf`) so it's not really clear how large the impact is in practice and it seems there are a few barriers to clear to use this to cause a DoS or other problems.

###### &ddagger; This would actually be quite problematic if it could occur because `glibc` seemingly only attempts to use `/dev/ptmx` when creating new terminals and thus most terminal managers (including `tmux`) and shell tools (including `sudo` -- but not `su`) would fail to start and thus bring the system to a halt. `setupPtmx` does add a symlink to `/dev/pts/ptmx` afterwards but on some systems the mode of the host `/dev/pts/ptmx` is set to `0o000` which would still cause the same DoS issue.

### Patches
This issue has been patched in runc 1.3.6, runc 1.4.3, and runc 1.5.0-rc.3.

### Workarounds
Using user namespaces restricts this attack fairly significantly such that the attacker can only create/delete inodes in directories that the remapped root user/group has write access to. Unless the root user is remapped to an actual user on the host (such as with rootless containers that don't use `/etc/sub[ug]id`), this in practice means that an attacker would only be able to create or delete inodes in world-writable directories.

LSMs can restrict the scope of where in the host filesystem runc can be tricked into operating on, though how much this helps is questionable. The default `container_runtime_t` SELinux label rules (or custom AppArmor rules for the host `runc` context) may restrict the scope where these filesystem operations can operate on, but we have not done an in-depth analysis on the impact of those kinds of LSM protections.

### Resources
* commit opencontainers/runc@864db8042dbb ("rootfs: make /dev initialisation code fd-based")
* https://github.com/containers/crun/security/advisories/GHSA-7vwr-4279-7gq5

### Credits
runc thanks "Davias" for initially finding and reporting this issue. The same underlying issue (with varying levels of completeness) was later reported by Arthur Chan (@arthurscchan from Ada Logics), Junyi Liu (@mosskappa), and Derek Manzella (@Dmanzella).

## References
- https://github.com/opencontainers/runc/security/advisories/GHSA-xjvp-4fhw-gc47
- https://github.com/opencontainers/runc
