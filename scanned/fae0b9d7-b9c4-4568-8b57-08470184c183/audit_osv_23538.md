# [H] IB/rdmavt: add lock to call to rvt_error_qp to prevent a race condition

## Summary
Severity: High
Advisory: CVE-2022-49089
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49089
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.189, >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

IB/rdmavt: add lock to call to rvt_error_qp to prevent a race condition

The documentation of the function rvt_error_qp says both r_lock and s_lock
need to be held when calling that function.  It also asserts using lockdep
that both of those locks are held.  However, the commit I referenced in
Fixes accidentally makes the call to rvt_error_qp in rvt_ruc_loopback no
longer covered by r_lock.  This results in the lockdep assertion failing
and also possibly in a race condition.

## References
- https://git.kernel.org/stable/c/43c2d7890ecabe527448a6c391fb2d9a5e6bbfe0
- https://git.kernel.org/stable/c/4d809f69695d4e7d1378b3a072fa9aef23123018
- https://git.kernel.org/stable/c/57800cc36e55db0547461c49acf5cd84c0f502b0
- https://git.kernel.org/stable/c/77ffb2495a41098f9d6a14f8aefde3188da75944
- https://git.kernel.org/stable/c/8a50937227c385a477177c9ffa122b4230e40666
- https://git.kernel.org/stable/c/92f1947c0d26060e978b3a9f21f32ce7c8c9cca3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49089.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49089
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
