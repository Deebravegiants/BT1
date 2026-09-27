# [H] bpf, arm64: Fix trampoline for BPF_TRAMP_F_CALL_ORIG

## Summary
Severity: High
Advisory: CVE-2024-43840
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43840
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.140, >=6.2.0 <6.6.92, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, arm64: Fix trampoline for BPF_TRAMP_F_CALL_ORIG

When BPF_TRAMP_F_CALL_ORIG is set, the trampoline calls
__bpf_tramp_enter() and __bpf_tramp_exit() functions, passing them
the struct bpf_tramp_image *im pointer as an argument in R0.

The trampoline generation code uses emit_addr_mov_i64() to emit
instructions for moving the bpf_tramp_image address into R0, but
emit_addr_mov_i64() assumes the address to be in the vmalloc() space
and uses only 48 bits. Because bpf_tramp_image is allocated using
kzalloc(), its address can use more than 48-bits, in this case the
trampoline will pass an invalid address to __bpf_tramp_enter/exit()
causing a kernel crash.

Fix this by using emit_a64_mov_i64() in place of emit_addr_mov_i64()
as it can work with addresses that are greater than 48-bits.

## References
- https://git.kernel.org/stable/c/077149478497b2f00ff4fd9da2c892defa6418d8
- https://git.kernel.org/stable/c/19d3c179a37730caf600a97fed3794feac2b197b
- https://git.kernel.org/stable/c/6d218fcc707d6b2c3616b6cd24b948fd4825cfec
- https://git.kernel.org/stable/c/d9664e6ff040798a46cdc5d401064f55b8676c83
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43840.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43840
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
