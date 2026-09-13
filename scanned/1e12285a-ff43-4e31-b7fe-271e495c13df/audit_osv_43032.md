# [H] HID: bpf: Fix hid_bpf_get_data() range check

## Summary
Severity: High
Advisory: CVE-2026-72352
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72352
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

HID: bpf: Fix hid_bpf_get_data() range check

hid_bpf_get_data() returns a pointer into the HID-BPF context data when
the caller-provided offset and size fit inside ctx->allocated_size.

The current check adds rdwr_buf_size and offset before comparing the
result against ctx->allocated_size. Since both values are unsigned, a
very large size can wrap the sum below ctx->allocated_size and make the
helper return a pointer even though the requested range is not contained
in the backing buffer.

Use check_add_overflow() to reject wrapped range ends before comparing
the requested range end against ctx->allocated_size.

## References
- https://git.kernel.org/stable/c/2d044049421dd48212b28646a850749d4a2d57fa
- https://git.kernel.org/stable/c/61a959b82f1aecd6d2d35c208013dd077cac9d10
- https://git.kernel.org/stable/c/ca373549140dfb386aa2de38364b58441b1f4885
- https://git.kernel.org/stable/c/f81bc5a709dcbaf2a3bbef4ca7167f93900cc39f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72352.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72352
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
