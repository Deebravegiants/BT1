# [H] comedi: Fix initialization of data for instructions that write to subdevice

## Summary
Severity: High
Advisory: CVE-2025-38478
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38478
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.29 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

comedi: Fix initialization of data for instructions that write to subdevice

Some Comedi subdevice instruction handlers are known to access
instruction data elements beyond the first `insn->n` elements in some
cases.  The `do_insn_ioctl()` and `do_insnlist_ioctl()` functions
allocate at least `MIN_SAMPLES` (16) data elements to deal with this,
but they do not initialize all of that.  For Comedi instruction codes
that write to the subdevice, the first `insn->n` data elements are
copied from user-space, but the remaining elements are left
uninitialized.  That could be a problem if the subdevice instruction
handler reads the uninitialized data.  Ensure that the first
`MIN_SAMPLES` elements are initialized before calling these instruction
handlers, filling the uncopied elements with 0.  For
`do_insnlist_ioctl()`, the same data buffer elements are used for
handling a list of instructions, so ensure the first `MIN_SAMPLES`
elements are initialized for each instruction that writes to the
subdevice.

## References
- https://git.kernel.org/stable/c/020eed5681d0f9bced73970368078a92d6cfaa9c
- https://git.kernel.org/stable/c/13e4d9038a1e869445a996a3f604a84ef52fe8f4
- https://git.kernel.org/stable/c/46d8c744136ce2454aa4c35c138cc06817f92b8e
- https://git.kernel.org/stable/c/673ee92bd2d31055bca98a1d96b653f5284289c4
- https://git.kernel.org/stable/c/6f38c6380c3b38a05032b8881e41137385a6ce02
- https://git.kernel.org/stable/c/c42116dc70af6664526f7aa82cf937824ab42649
- https://git.kernel.org/stable/c/d3436638738ace8f101af7bdee2eae1bc38e9b29
- https://git.kernel.org/stable/c/fe8713fb4e4e82a4f91910d9a41bf0613e69a0b9
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38478.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38478
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
