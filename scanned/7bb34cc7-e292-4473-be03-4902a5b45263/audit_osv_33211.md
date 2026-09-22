# [H] accel/ivpu: Prevent recovery work from being queued during device removal

## Summary
Severity: High
Advisory: CVE-2025-39896
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39896
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ivpu: Prevent recovery work from being queued during device removal

Use disable_work_sync() instead of cancel_work_sync() in ivpu_dev_fini()
to ensure that no new recovery work items can be queued after device
removal has started. Previously, recovery work could be scheduled even
after canceling existing work, potentially leading to use-after-free
bugs if recovery accessed freed resources.

Rename ivpu_pm_cancel_recovery() to ivpu_pm_disable_recovery() to better
reflect its new behavior.

## References
- https://git.kernel.org/stable/c/54c49eca38dbd06913a696f6d7610937dcfad226
- https://git.kernel.org/stable/c/565d2c15b6c36c3250e694f7b9a86229c1787be5
- https://git.kernel.org/stable/c/69a79ada8eb034ce016b5b78fb7d08d8687223de
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39896.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39896
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
