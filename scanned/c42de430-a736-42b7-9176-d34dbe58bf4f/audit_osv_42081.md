# [H] 6lowpan: fix NHC entry use-after-free on error path

## Summary
Severity: High
Advisory: CVE-2026-64452
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:A/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64452
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

6lowpan: fix NHC entry use-after-free on error path

lowpan_nhc_do_uncompression() looks up an NHC descriptor while holding
lowpan_nhc_lock.  If the descriptor has no uncompress callback, the error
path drops the lock before printing nhc->name.

lowpan_nhc_del() removes descriptors under the same lock and then relies
on synchronize_net() before the owning module can be unloaded.  That only
waits for net RX RCU readers.  lowpan_header_decompress() is also exported
and can be reached from callers that are not necessarily covered by the net
core RX critical section, for example the Bluetooth 6LoWPAN L2CAP receive
path.

This leaves a race where one task drops lowpan_nhc_lock in the error path,
another task unregisters and frees the matching descriptor after
synchronize_net() returns, and the first task then dereferences nhc->name
for the warning.

With the post-unlock window widened, KASAN reports:

  BUG: KASAN: slab-use-after-free in lowpan_nhc_do_uncompression+0x1f4/0x220
  Read of size 8
  lowpan_nhc_do_uncompression
  lowpan_header_decompress

Fix this by printing the warning before dropping lowpan_nhc_lock, so the
descriptor name is read while unregister is still excluded.  The malformed
packet is still rejected with -ENOTSUPP.

## References
- https://git.kernel.org/stable/c/0beccbcf50de125be5520d0ffc59af4bb8655482
- https://git.kernel.org/stable/c/1720db928e5a58ca7d75ac1d514c3b73fd7061a7
- https://git.kernel.org/stable/c/593b78bb3c7ef0c6e9ae6fdf5afa80a5f7573168
- https://git.kernel.org/stable/c/80b5c8779acee0550845394fb3e5176a398aa24c
- https://git.kernel.org/stable/c/9c2f5c0829a8c8b904dae36be6d8056b719ac605
- https://git.kernel.org/stable/c/a8e3a94711134e898c6021a6b77374efa91b3639
- https://git.kernel.org/stable/c/b713aa0cc344f10f7a9928a230b5f5e780d04078
- https://git.kernel.org/stable/c/cc27aea4d454abfb385ee2c9499c78b96db9b728
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64452.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64452
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
