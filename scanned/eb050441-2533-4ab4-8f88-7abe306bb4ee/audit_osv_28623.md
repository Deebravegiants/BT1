# [H] tee: optee: Fix kernel panic caused by incorrect error handling

## Summary
Severity: High
Advisory: CVE-2024-35785
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35785
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.84, >=6.2.0 <6.6.24, >=6.7.0 <6.7.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

tee: optee: Fix kernel panic caused by incorrect error handling

The error path while failing to register devices on the TEE bus has a
bug leading to kernel panic as follows:

[   15.398930] Unable to handle kernel paging request at virtual address ffff07ed00626d7c
[   15.406913] Mem abort info:
[   15.409722]   ESR = 0x0000000096000005
[   15.413490]   EC = 0x25: DABT (current EL), IL = 32 bits
[   15.418814]   SET = 0, FnV = 0
[   15.421878]   EA = 0, S1PTW = 0
[   15.425031]   FSC = 0x05: level 1 translation fault
[   15.429922] Data abort info:
[   15.432813]   ISV = 0, ISS = 0x00000005, ISS2 = 0x00000000
[   15.438310]   CM = 0, WnR = 0, TnD = 0, TagAccess = 0
[   15.443372]   GCS = 0, Overlay = 0, DirtyBit = 0, Xs = 0
[   15.448697] swapper pgtable: 4k pages, 48-bit VAs, pgdp=00000000d9e3e000
[   15.455413] [ffff07ed00626d7c] pgd=1800000bffdf9003, p4d=1800000bffdf9003, pud=0000000000000000
[   15.464146] Internal error: Oops: 0000000096000005 [#1] PREEMPT SMP

Commit 7269cba53d90 ("tee: optee: Fix supplicant based device enumeration")
lead to the introduction of this bug. So fix it appropriately.

## References
- https://git.kernel.org/stable/c/4b12ff5edd141926d49c9ace4791adf3a4902fe7
- https://git.kernel.org/stable/c/520f79c110ff712b391b3d87fcacf03c74bc56ee
- https://git.kernel.org/stable/c/95915ba4b987cf2b222b0f251280228a1ff977ac
- https://git.kernel.org/stable/c/bc40ded92af55760d12bec8222d4108de725dbe4
- https://git.kernel.org/stable/c/bfa344afbe472a9be08f78551fa2190c1a07d7d3
- https://git.kernel.org/stable/c/e5b5948c769aa1ebf962dddfb972f87d8f166f95
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35785.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35785
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
