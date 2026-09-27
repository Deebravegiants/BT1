# [H] ipvs: clear the svc scheduler ptr early on edit

## Summary
Severity: High
Advisory: CVE-2026-53270
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53270
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: clear the svc scheduler ptr early on edit

ip_vs_edit_service() while unbinding the old scheduler clears
the svc->scheduler ptr after the scheduler module initiates
RCU callbacks. This can cause packets to use the old
scheduler at the time when svc->sched_data is already freed
after RCU grace period.

Fix it by clearing the ptr early in ip_vs_unbind_scheduler(),
before the done_service method schedules any RCU callbacks.

Also, if the new scheduler fails to initialize when replacing
the old scheduler, try to restore the old scheduler while still
returning the error code.

## References
- https://git.kernel.org/stable/c/14e4689c113b4c06af1069364ade24fdd7055f33
- https://git.kernel.org/stable/c/193989cc6d80dd8e0460fb3992e69fa03bf0ff9b
- https://git.kernel.org/stable/c/19a9493faa4bf3c7bd0a386f30b60b1bb4a3da03
- https://git.kernel.org/stable/c/25918720ba97f974a4f8d433b5a0132c5b43f6f3
- https://git.kernel.org/stable/c/7d4f5004511757e3984901ffb412fcf858d80ed5
- https://git.kernel.org/stable/c/c6376b9b1b4d2bad638256b1b3588e073344ae69
- https://git.kernel.org/stable/c/d10730a1f2caf08088e0db1b19b242f3e6fa5f06
- https://git.kernel.org/stable/c/e4feec3174036ba772006be74beee0efa09a9eb8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53270.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53270
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
