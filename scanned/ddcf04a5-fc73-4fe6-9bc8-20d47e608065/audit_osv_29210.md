# [H] powerpc/pseries: Enforce hcall result buffer validity and size

## Summary
Severity: High
Advisory: CVE-2024-40974
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40974
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.96, >=6.2.0 <6.6.36, >=6.7.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/pseries: Enforce hcall result buffer validity and size

plpar_hcall(), plpar_hcall9(), and related functions expect callers to
provide valid result buffers of certain minimum size. Currently this
is communicated only through comments in the code and the compiler has
no idea.

For example, if I write a bug like this:

  long retbuf[PLPAR_HCALL_BUFSIZE]; // should be PLPAR_HCALL9_BUFSIZE
  plpar_hcall9(H_ALLOCATE_VAS_WINDOW, retbuf, ...);

This compiles with no diagnostics emitted, but likely results in stack
corruption at runtime when plpar_hcall9() stores results past the end
of the array. (To be clear this is a contrived example and I have not
found a real instance yet.)

To make this class of error less likely, we can use explicitly-sized
array parameters instead of pointers in the declarations for the hcall
APIs. When compiled with -Warray-bounds[1], the code above now
provokes a diagnostic like this:

error: array argument is too small;
is of size 32, callee requires at least 72 [-Werror,-Warray-bounds]
   60 |                 plpar_hcall9(H_ALLOCATE_VAS_WINDOW, retbuf,
      |                 ^                                   ~~~~~~

[1] Enabled for LLVM builds but not GCC for now. See commit
    0da6e5fd6c37 ("gcc: disable '-Warray-bounds' for gcc-13 too") and
    related changes.

## References
- https://git.kernel.org/stable/c/19c166ee42cf16d8b156a6cb4544122d9a65d3ca
- https://git.kernel.org/stable/c/262e942ff5a839b9e4f3302a8987928b0c8b8a2d
- https://git.kernel.org/stable/c/3ad0034910a57aa88ed9976b1431b7b8c84e0048
- https://git.kernel.org/stable/c/8aa11aa001576bf3b00dcb8559564ad7a3113588
- https://git.kernel.org/stable/c/a8c988d752b3d98d5cc1e3929c519a55ef55426c
- https://git.kernel.org/stable/c/aa6107dcc4ce9a3451f2d729204713783b657257
- https://git.kernel.org/stable/c/acf2b80c31c37acab040baa3cf5f19fbd5140b18
- https://git.kernel.org/stable/c/ff2e185cf73df480ec69675936c4ee75a445c3e4
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40974.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40974
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
