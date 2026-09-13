# [H] pstore/ram: Check start of empty przs during init

## Summary
Severity: High
Advisory: CVE-2023-53331
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53331
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.0.0 <5.10.195, >=5.5.0 <5.15.132, >=5.11.0 <6.1.53, >=5.16.0 <6.4.16, >=6.2.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

pstore/ram: Check start of empty przs during init

After commit 30696378f68a ("pstore/ram: Do not treat empty buffers as
valid"), initialization would assume a prz was valid after seeing that
the buffer_size is zero (regardless of the buffer start position). This
unchecked start value means it could be outside the bounds of the buffer,
leading to future access panics when written to:

 sysdump_panic_event+0x3b4/0x5b8
 atomic_notifier_call_chain+0x54/0x90
 panic+0x1c8/0x42c
 die+0x29c/0x2a8
 die_kernel_fault+0x68/0x78
 __do_kernel_fault+0x1c4/0x1e0
 do_bad_area+0x40/0x100
 do_translation_fault+0x68/0x80
 do_mem_abort+0x68/0xf8
 el1_da+0x1c/0xc0
 __raw_writeb+0x38/0x174
 __memcpy_toio+0x40/0xac
 persistent_ram_update+0x44/0x12c
 persistent_ram_write+0x1a8/0x1b8
 ramoops_pstore_write+0x198/0x1e8
 pstore_console_write+0x94/0xe0
 ...

To avoid this, also check if the prz start is 0 during the initialization
phase. If not, the next prz sanity check case will discover it (start >
size) and zap the buffer back to a sane state.

[kees: update commit log with backtrace and clarifications]

## References
- https://git.kernel.org/stable/c/25fb4e3402d46f425ec135ef6f09792a4c1b3003
- https://git.kernel.org/stable/c/89312657337e6e03ad6e9ea1a462bd9c158c85c8
- https://git.kernel.org/stable/c/c807ccdd812d18985860504b503899f3140a9549
- https://git.kernel.org/stable/c/dc2f60de9a7d3efd982440117dab5579898d808c
- https://git.kernel.org/stable/c/e95d7a8a6edd14f8fab44c777dd7281db91f6ae2
- https://git.kernel.org/stable/c/e972231db29b5d1dccc13bf9d5ba55b6979a69ed
- https://git.kernel.org/stable/c/f77990358628b01bdc03752126ff5f716ea37615
- https://git.kernel.org/stable/c/fe8c3623ab06603eb760444a032d426542212021
- https://git.kernel.org/stable/c/fedecaeef88899d940b69368c996e8b3b0b8650d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53331.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53331
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
