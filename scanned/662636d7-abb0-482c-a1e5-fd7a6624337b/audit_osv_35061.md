# [H] jfs: fix uninitialized waitqueue in transaction manager

## Summary
Severity: High
Advisory: CVE-2025-68168
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68168
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.302, >=5.5.0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=6.2.0 <6.6.117, >=6.5.0 <6.12.58, >=6.7.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: fix uninitialized waitqueue in transaction manager

The transaction manager initialization in txInit() was not properly
initializing TxBlock[0].waitor waitqueue, causing a crash when
txEnd(0) is called on read-only filesystems.

When a filesystem is mounted read-only, txBegin() returns tid=0 to
indicate no transaction. However, txEnd(0) still gets called and
tries to access TxBlock[0].waitor via tid_to_tblock(0), but this
waitqueue was never initialized because the initialization loop
started at index 1 instead of 0.

This causes a 'non-static key' lockdep warning and system crash:
  INFO: trying to register non-static key in txEnd

Fix by ensuring all transaction blocks including TxBlock[0] have
their waitqueues properly initialized during txInit().

## References
- https://git.kernel.org/stable/c/038861414ab383b41dd35abbf9ff0ef715592d53
- https://git.kernel.org/stable/c/2a9575a372182ca075070b3cd77490dcf0c951e7
- https://git.kernel.org/stable/c/300b072df72694ea330c4c673c035253e07827b8
- https://git.kernel.org/stable/c/8cae9cf23e0bd424ac904e753639a587543ce03a
- https://git.kernel.org/stable/c/a2aa97cde9857f881920635a2e3d3b11769619c5
- https://git.kernel.org/stable/c/cbf2f527ae4ca7c7dabce42e85e8deb58588a37e
- https://git.kernel.org/stable/c/d2dd7ca05a11685c314e62802a55e8d67a90e974
- https://git.kernel.org/stable/c/d6af7fce2e162ac68e85d3a11eb6ac8c35b24b64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68168.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68168
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
