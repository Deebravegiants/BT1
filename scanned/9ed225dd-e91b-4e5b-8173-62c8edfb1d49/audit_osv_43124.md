# [C] RDMA/irdma: Replace waitqueue and flag with completion

## Summary
Severity: Critical
Advisory: CVE-2026-72494
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72494
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/irdma: Replace waitqueue and flag with completion

The driver previously used a waitqueue along with an explicit
request_done flag, but without proper barriers around request_done.

An earlier patch by Gui-Dong Han <hanguidong02@gmail.com> attempted
to fix this by adding the missing memory barriers. Rather than
adding the barriers, this patch replaces the waitqueue+flag with
a completion, which is designed for this exact purpose.

## References
- https://git.kernel.org/stable/c/bde37aed0724c0139dea177f3aae8d989b6babb1
- https://git.kernel.org/stable/c/d9c8c45e6d2f438a3c8e643ae78b59454fa0fadd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72494.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72494
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
