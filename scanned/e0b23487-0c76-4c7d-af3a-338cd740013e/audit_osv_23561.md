# [H] ref_tracker: implement use-after-free detection

## Summary
Severity: High
Advisory: CVE-2022-49127
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49127
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ref_tracker: implement use-after-free detection

Whenever ref_tracker_dir_init() is called, mark the struct ref_tracker_dir
as dead.

Test the dead status from ref_tracker_alloc() and ref_tracker_free()

This should detect buggy dev_put()/dev_hold() happening too late
in netdevice dismantle process.

## References
- https://git.kernel.org/stable/c/3743c9de303fa36c2e2ca2522ab280c52bcafbd2
- https://git.kernel.org/stable/c/e3ececfe668facd87d920b608349a32607060e66
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49127.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49127
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
