# [H] wifi: rt2x00: avoid full teardown before work setup in probe

## Summary
Severity: High
Advisory: CVE-2026-72005
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72005
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: rt2x00: avoid full teardown before work setup in probe

rt2x00lib_probe_dev() uses the full rt2x00lib_remove_dev() teardown for
all probe failures. However, drv_data allocation and workqueue allocation
can fail before intf_work, autowakeup_work and sleep_work have been
initialized.

Do not enter the full remove path until the probe has reached the point
where those work items are set up. Return directly for drv_data allocation
failure, and use a small early cleanup path for workqueue allocation
failure.

This issue was found by our static analysis tool and then confirmed by
manual review of rt2x00lib_probe_dev() and rt2x00lib_remove_dev(). The
early probe exits should not call a common teardown path that assumes the
later work setup has already completed.

A QEMU PoC forced alloc_ordered_workqueue() to fail before the work
initializers are reached. The resulting fail path entered
rt2x00lib_remove_dev(), and DEBUG_OBJECTS reported invalid work drains with
rt2x00lib_probe_dev() and rt2x00lib_remove_dev() in the stack.

## References
- https://git.kernel.org/stable/c/3c0427d719bddb33caf18ff4ffb77cb47de7eb00
- https://git.kernel.org/stable/c/536fb3d739d75a03cb318c0c6fe799425cfea501
- https://git.kernel.org/stable/c/56994852d704535ea354a4627ca667b1b4fa0deb
- https://git.kernel.org/stable/c/59afe6148927395cf86f9429900e029a48b1d42b
- https://git.kernel.org/stable/c/66bd9b1a72de7c2f5141b02d796048aafaed8a49
- https://git.kernel.org/stable/c/816559409e340acaa5c9d868291dab30d8c80263
- https://git.kernel.org/stable/c/8b58d1f1356df6a7d2de3f55bb665b18b04ffda0
- https://git.kernel.org/stable/c/eb7474d0253bb2de4793e1d3ce833e8564bbe732
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72005.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72005
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
