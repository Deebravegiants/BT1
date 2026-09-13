# [H] pwrseq: core: fix use-after-free in pwrseq_debugfs_seq_next()

## Summary
Severity: High
Advisory: CVE-2026-64251
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-64251
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

pwrseq: core: fix use-after-free in pwrseq_debugfs_seq_next()

pwrseq_debugfs_seq_next() declares 'next' with __free(put_device),
which causes put_device() to be called on the returned pointer when
the variable goes out of scope.  This results in a use-after-free
since the seq_file framework receives a pointer whose reference has
already been dropped.

Simply removing __free(put_device) would fix the UAF but would leak
the reference acquired by bus_find_next_device(), as stop() only
calls up_read(&pwrseq_sem) and never releases the device reference.

Fix this by making the reference counting consistent across all
seq_file callbacks, matching the standard pattern used by PCI and
SCSI:

- start(): use get_device() so it returns a referenced pointer.
- next(): explicitly put_device(curr) to release the previous
  device's reference (no NULL check needed - the seq_file framework
  only calls next() while the previous return was non-NULL).
- stop(): put_device(data) to release the last iterated device's
  reference, with a NULL guard since stop() may be called with NULL
  when start() returned NULL or next() reached end-of-sequence.

## References
- https://git.kernel.org/stable/c/257595adf9dac15ae1edd9d07753fbc576a7583d
- https://git.kernel.org/stable/c/73569a44fca2992f0ca4a4c0104069741b9873a0
- https://git.kernel.org/stable/c/ba0b9f04c7a5f9887b8ce672eaf049502c0548ec
- https://git.kernel.org/stable/c/e91df6d273445c03f5aa302bfe147eda33d45794
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64251.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64251
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
