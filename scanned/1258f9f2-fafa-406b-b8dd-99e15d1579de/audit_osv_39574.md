# [H] RDMA/vmw_pvrdma: Fix double free on pvrdma_alloc_ucontext() error path

## Summary
Severity: High
Advisory: CVE-2026-46189
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46189
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/vmw_pvrdma: Fix double free on pvrdma_alloc_ucontext() error path

Sashiko points out that pvrdma_uar_free() is already called within
pvrdma_dealloc_ucontext(), so calling it before triggers a double free.

## References
- https://git.kernel.org/stable/c/0c63333ff97bd1275294fd12840a0efe9d7a4c59
- https://git.kernel.org/stable/c/1df5711121cdc11e76b889408fdbe459feba1d39
- https://git.kernel.org/stable/c/269967d7693304e1f06ed2dff4ebbbeeb397cda4
- https://git.kernel.org/stable/c/3a231c34c5bc3d3cfc850b877758ec9fdaa8a483
- https://git.kernel.org/stable/c/45d25e3ec17900bf5a9d6876ff16ceee31c4c0e0
- https://git.kernel.org/stable/c/935ee27d0904aa944cbcc979094c20e5ef62eead
- https://git.kernel.org/stable/c/e38e86995df27f1f854063dab1f0c6a513db3faf
- https://git.kernel.org/stable/c/ecc36a82ecfcfdf3c6606d209f22ec5543c410e0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46189.json
- https://access.redhat.com/errata/RHSA-2026:30848
- https://access.redhat.com/errata/RHSA-2026:33685
- https://access.redhat.com/errata/RHSA-2026:33743
- https://access.redhat.com/errata/RHSA-2026:35904
- https://access.redhat.com/errata/RHSA-2026:36049
- https://access.redhat.com/errata/RHSA-2026:36073
- https://access.redhat.com/errata/RHSA-2026:36767
- https://access.redhat.com/errata/RHSA-2026:38902
- https://access.redhat.com/errata/RHSA-2026:40068
- https://access.redhat.com/errata/RHSA-2026:40760
- https://access.redhat.com/errata/RHSA-2026:47633
