# [H] Drivers: hv: vmbus: Deactivate sysctl_record_panic_msg by default in isolated guests

## Summary
Severity: High
Advisory: CVE-2022-49054
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49054
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.35, >=5.16.0 <5.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Drivers: hv: vmbus: Deactivate sysctl_record_panic_msg by default in isolated guests

hv_panic_page might contain guest-sensitive information, do not dump it
over to Hyper-V by default in isolated guests.

While at it, update some comments in hyperv_{panic,die}_event().

## References
- https://git.kernel.org/stable/c/1b576e81d31b56b248316b8ff816b1cc5c4407c7
- https://git.kernel.org/stable/c/6230bc50d6d21cae4c084766623d0a6d17958721
- https://git.kernel.org/stable/c/9f8b577f7b43b2170628d6c537252785dcc2dcea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49054.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49054
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
