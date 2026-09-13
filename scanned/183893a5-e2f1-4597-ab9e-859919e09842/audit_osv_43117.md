# [H] coresight: platform: defer connection counter increment until alloc succeeds

## Summary
Severity: High
Advisory: CVE-2026-72485
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72485
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

coresight: platform: defer connection counter increment until alloc succeeds

coresight_add_out_conn() increments nr_outconns before calling
devm_krealloc_array() and again before devm_kmalloc(). If either
allocation fails, the counter is already bumped while the corresponding
array entry is NULL or uninitialized garbage.

coresight_add_in_conn() has the same problem with nr_inconns and
devm_krealloc_array().

In both cases the probe returns -ENOMEM, which causes
coresight_get_platform_data() to call coresight_release_platform_data()
for cleanup. That function iterates up to nr_outconns (or nr_inconns)
entries and dereferences each pointer unconditionally, hitting the NULL
or garbage entry and panicking instead of failing gracefully.

Fix by moving the counter increments to after all allocations succeed,
so the struct is always consistent on any error path.

## References
- https://git.kernel.org/stable/c/1563ae33dc4f5ebac96b93af2ef72e72aaaa31ae
- https://git.kernel.org/stable/c/8ca9adc805884d3bb5038082462577f86c2c4a10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72485.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72485
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
