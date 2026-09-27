# [M] RDMA/irdma: Prevent some integer underflows

## Summary
Severity: Medium
Advisory: CVE-2022-49208
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49208
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Prevent some integer underflows

My static checker complains that:

    drivers/infiniband/hw/irdma/ctrl.c:3605 irdma_sc_ceq_init()
    warn: can subtract underflow 'info->dev->hmc_fpm_misc.max_ceqs'?

It appears that "info->dev->hmc_fpm_misc.max_ceqs" comes from the firmware
in irdma_sc_parse_fpm_query_buf() so, yes, there is a chance that it could
be zero.  Even if we trust the firmware, it's easy enough to change the
condition just as a hardenning measure.

## References
- https://git.kernel.org/stable/c/6f6dbb819dfc1a35bcb8b709b5c83a3ea8beff75
- https://git.kernel.org/stable/c/7340c3675d7ac946f4019b84cd7c64ed542dfe4c
- https://git.kernel.org/stable/c/d52dab6e03550f9c97121b0c11c0a3ed78ee76a4
- https://git.kernel.org/stable/c/f21056f15bbeacab7b4b87af232f5599d1f2bff1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49208.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49208
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
