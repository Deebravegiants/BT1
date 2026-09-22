# [H] RDMA/irdma: Prevent rereg_mr for non-mem regions

## Summary
Severity: High
Advisory: CVE-2026-68419
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68419
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.148, >=6.7.0 <6.18.42, >=6.13.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Prevent rereg_mr for non-mem regions

When a QP/CQ/SRQ is created, a two step process is used
where the buffer is allocated in userspace and explicitly
registered with the normal reg_mr mechanism prior to creating
the actual QP/CQ/SRQ object.

These special registrations are indicated via an ABI field
so the driver knows that they do not have a valid mkey and
to skip the actual CQP command submission.

Since these are real MR objects from the core's perspective,
it is possible for a user application to invoke rereg_mr on them
and cause a real CQP op to be emitted with the zero-initialized
mkey value of 0.

Fix this by preventing rereg_mr on these special regions.

## References
- https://git.kernel.org/stable/c/a846aecb931b4d65d5eafa92a0623545af46d4f2
- https://git.kernel.org/stable/c/b5029e91c63406e4f4c8d58161048b41b6f0bd8c
- https://git.kernel.org/stable/c/ca1c29f05274b737dc964e28b97803750d7cf7ec
- https://git.kernel.org/stable/c/dbaa37e060918c45517786e37ecab0f300b48fa9
- https://git.kernel.org/stable/c/fb46d134e1b8690bed2da9005b36d32d2efd34ac
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68419.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68419
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
