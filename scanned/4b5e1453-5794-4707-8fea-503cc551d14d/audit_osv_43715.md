# [H] vsock/virtio: read virtqueues under worker locks

## Summary
Severity: High
Advisory: CVE-2026-74614
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74614
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.216, >=5.16.0 <6.1.183, >=5.19.0 <6.6.152, >=6.2.0 <6.12.104, >=6.7.0 <6.18.45, >=6.13.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/virtio: read virtqueues under worker locks

Commit bd50c5dc182b ("vsock/virtio: add support for device
suspend/resume") made the *_run flags transition from false to true when
restore installs replacement virtqueues.  The RX, TX and event workers
read their virtqueue before locking and checking the corresponding flag,
so a worker delayed across freeze and restore can observe the replacement
queue's running state while retaining a pointer to the deleted queue.

Read each virtqueue under its mutex after checking the run flag, keeping
the pointer and state in the same queue generation.

## References
- https://git.kernel.org/stable/c/1cecb4202afdbeddcf29d59baf596ac6ab753f7f
- https://git.kernel.org/stable/c/29dd10583bf9d2744cd84b862e4257c0a5699570
- https://git.kernel.org/stable/c/941329ce14c5f481223a10d1d4c8b57ea7f3048a
- https://git.kernel.org/stable/c/a1fb0c5b8a7c2753758aeced40971f99449dde0c
- https://git.kernel.org/stable/c/bd43a7ec668be428265b3209eb43647aedcf720a
- https://git.kernel.org/stable/c/eae099c764c7ebdb842eb1f638913e310bdd6513
- https://git.kernel.org/stable/c/ebac8f6b1ef0e9278afe204b8692a7479988dace
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74614.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74614
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
