# [H] bpf: Reject %p% format string in bprintf-like helpers

## Summary
Severity: High
Advisory: CVE-2025-38528
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38528
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Reject %p% format string in bprintf-like helpers

static const char fmt[] = "%p%";
    bpf_trace_printk(fmt, sizeof(fmt));

The above BPF program isn't rejected and causes a kernel warning at
runtime:

    Please remove unsupported %\x00 in format string
    WARNING: CPU: 1 PID: 7244 at lib/vsprintf.c:2680 format_decode+0x49c/0x5d0

This happens because bpf_bprintf_prepare skips over the second %,
detected as punctuation, while processing %p. This patch fixes it by
not skipping over punctuation. %\x00 is then processed in the next
iteration and rejected.

## References
- https://git.kernel.org/stable/c/1c5f5fd47bbda17cb885fe6f03730702cd53d3f8
- https://git.kernel.org/stable/c/61d5fa45ed13e42af14c7e959baba9908b8ee6d4
- https://git.kernel.org/stable/c/6952aeace93f8c9ea01849efecac24dd3152c9c9
- https://git.kernel.org/stable/c/97303e541e12f1fea97834ec64b98991e8775f39
- https://git.kernel.org/stable/c/e7be679124bae8cf4fa6e40d7e1661baddfb3289
- https://git.kernel.org/stable/c/f8242745871f81a3ac37f9f51853d12854fd0b58
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38528.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38528
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
