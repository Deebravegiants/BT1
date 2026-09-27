# [H] ACPICA: Fix error code path in acpi_ds_call_control_method()

## Summary
Severity: High
Advisory: CVE-2022-50411
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50411
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPICA: Fix error code path in acpi_ds_call_control_method()

A use-after-free in acpi_ps_parse_aml() after a failing invocaion of
acpi_ds_call_control_method() is reported by KASAN [1] and code
inspection reveals that next_walk_state pushed to the thread by
acpi_ds_create_walk_state() is freed on errors, but it is not popped
from the thread beforehand.  Thus acpi_ds_get_current_walk_state()
called by acpi_ps_parse_aml() subsequently returns it as the new
walk state which is incorrect.

To address this, make acpi_ds_call_control_method() call
acpi_ds_pop_walk_state() to pop next_walk_state from the thread before
returning an error.

## References
- https://git.kernel.org/stable/c/0462fec709d51762ba486245bc344f44cc6cfa97
- https://git.kernel.org/stable/c/2deb42c4f9776e59bee247c14af9c5e8c05ca9a6
- https://git.kernel.org/stable/c/38e251d356a01b61a86cb35213cafd7e8fe7090c
- https://git.kernel.org/stable/c/404ec60438add1afadaffaed34bb5fe4ddcadd40
- https://git.kernel.org/stable/c/5777432ebaaf797e24f059979b42df3139967163
- https://git.kernel.org/stable/c/799881db3e03b5e98fe6a900d9d7de8c7d61e7ee
- https://git.kernel.org/stable/c/9ef353c92f9d04c88de3af1a46859c1fb76db0f8
- https://git.kernel.org/stable/c/b0b83d3f3ffa96e8395c56b83d6197e184902a34
- https://git.kernel.org/stable/c/f520d181477ec29a496c0b3bbfbdb7e2606c2713
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50411.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50411
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
