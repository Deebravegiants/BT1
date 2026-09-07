# [H] LXD vulnerable to a local privilege escalation through custom storage volumes

## Summary
Severity: High
Advisory: GHSA-3g2j-vm47-x4mj
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-3g2j-vm47-x4mj
Type: github-advisory

## Affected
- Go: `github.com/canonical/lxd` — affected >=0 <0.0.0-20251110144034-698854d0164f

## Details
**Impact**

This affects any LXD user in an environment where an unprivileged user may have root access to a container with an attached custom storage volume that has the `security.shifted` property set to `true` as well as access to the host as an unprivileged user.

The most common case for this would be systems using `lxd-user` with the less privileged lxd group to provide unprivileged users with an isolated restricted access to LXD. Such users may be able to create a custom storage volume with the necessary property (depending on kernel and filesystem support) and can then write a setuid binary from within the container which can be executed as an unprivileged user on the host to gain root privileges.

**Patches**

Patches for this issue are available: 

- LXD 6 series: https://github.com/canonical/lxd/pull/16904
- LXD 5.21 LTS series: https://github.com/canonical/lxd/pull/16922
- LXD 5.0 LTS series: https://github.com/canonical/lxd/pull/16923
- LXD 4.0 LTS series: https://github.com/canonical/lxd/pull/16924 

The first commit changes the permissions for any new storage pool, the later commit adds a patch that applies it on startup to all existing storage pools.

These fixes are also available in the associated candidate snap channels for each LTS series:

- 5.21/candidate (5.21.4-8a3cf61)
- 5.0/candidate (5.0.5-5c60378)
- 4.0/candidate (4.0.10-35a8127)

We will be preparing intermediate releases to the associated stable snap channels shortly.

**Workarounds**

Permissions can be manually restricted until a patched version of LXD is deployed.

This is done with:

```
sudo nsenter --mount=/run/snapd/ns/lxd.mnt -- chmod 0700 /var/snap/lxd/common/lxd/storage-pools/*/{custom*,virtual-machines*,images}
sudo nsenter --mount=/run/snapd/ns/lxd.mnt -- chmod 0711 /var/snap/lxd/common/lxd/storage-pools/*/{containers*,buckets*}
```

Those are the same permissions which will be applied by the patched LXD for both new and existing storage pools.

**References**

This was reported to Incus publicly on Github here: 

- https://github.com/lxc/incus/security/advisories/GHSA-56mx-8g9f-5crf
- https://github.com/lxc/incus/issues/2641

## References
- https://github.com/canonical/lxd/security/advisories/GHSA-3g2j-vm47-x4mj
- https://github.com/lxc/incus/security/advisories/GHSA-56mx-8g9f-5crf
- https://github.com/lxc/incus/issues/2641
- https://github.com/canonical/lxd/pull/16904
- https://github.com/canonical/lxd/pull/16922
- https://github.com/canonical/lxd/pull/16923
- https://github.com/canonical/lxd/pull/16924
- https://github.com/canonical/lxd
