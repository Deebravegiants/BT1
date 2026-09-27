# [C] KVM: SEV: Compute the correct max length of the in-GHCB scratch area

## Summary
Severity: Critical
Advisory: CVE-2026-63939
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63939
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SEV: Compute the correct max length of the in-GHCB scratch area

When setting the length of the GHCB scratch area, and the area is in the
GHCB shared buffer, set the effective length of the scratch area to the max
possible size given the start of the guest-provided pointer, and the end of
the shared buffer.

The code was "fine" when first introduced, as KVM doesn't consult the
length of the buffer when emulating MMIO, because the passed in @len always
specifies the *max* size required.  But for PSC requests, the incoming @len
is just the minimum length (to process the header), and KVM needs to know
the full size of the scratch area to avoid buffer overflows (spoiler alert).

Opportunistically rename @len => @min_len to better reflect its role.

## References
- https://git.kernel.org/stable/c/5867d7e202e09f037cefe77f7af4413c7c0fa088
- https://git.kernel.org/stable/c/6644565527c4c5f507088b1c9ddf72de47790b68
- https://git.kernel.org/stable/c/6ca9400d36005ffdca25f80186bea781c7e1dc4c
- https://git.kernel.org/stable/c/9f0a9e780f02c02d025a190f1885e1d1d73b87bd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63939.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63939
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
