# [H] usb: xhci: Fix invalid pointer dereference in Etron workaround

## Summary
Severity: High
Advisory: CVE-2025-37813
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-08
Source: https://osv.dev/vulnerability/CVE-2025-37813
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: xhci: Fix invalid pointer dereference in Etron workaround

This check is performed before prepare_transfer() and prepare_ring(), so
enqueue can already point at the final link TRB of a segment. And indeed
it will, some 0.4% of times this code is called.

Then enqueue + 1 is an invalid pointer. It will crash the kernel right
away or load some junk which may look like a link TRB and cause the real
link TRB to be replaced with a NOOP. This wouldn't end well.

Use a functionally equivalent test which doesn't dereference the pointer
and always gives correct result.

Something has crashed my machine twice in recent days while playing with
an Etron HC, and a control transfer stress test ran for confirmation has
just crashed it again. The same test passes with this patch applied.

## References
- https://git.kernel.org/stable/c/0624e29c595b05e7a0e6d1c368f0a05799928e30
- https://git.kernel.org/stable/c/142273a49f2c315eabdbdf5a71c15e479b75ca91
- https://git.kernel.org/stable/c/1ea050da5562af9b930d17cbbe9632d30f5df43a
- https://git.kernel.org/stable/c/bce3055b08e303e28a8751f6073066f5c33a0744
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37813.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37813
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
