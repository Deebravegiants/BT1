# [H] lib: cpu_rmap: Avoid use after free on rmap->obj array entries

## Summary
Severity: High
Advisory: CVE-2023-53484
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53484
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.8.0 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

lib: cpu_rmap: Avoid use after free on rmap->obj array entries

When calling irq_set_affinity_notifier() with NULL at the notify
argument, it will cause freeing of the glue pointer in the
corresponding array entry but will leave the pointer in the array. A
subsequent call to free_irq_cpu_rmap() will try to free this entry again
leading to possible use after free.

Fix that by setting NULL to the array entry and checking that we have
non-zero at the array entry when iterating over the array in
free_irq_cpu_rmap().

The current code does not suffer from this since there are no cases
where irq_set_affinity_notifier(irq, NULL) (note the NULL passed for the
notify arg) is called, followed by a call to free_irq_cpu_rmap() so we
don't hit and issue. Subsequent patches in this series excersize this
flow, hence the required fix.

## References
- https://git.kernel.org/stable/c/4e0473f1060aa49621d40a113afde24818101d37
- https://git.kernel.org/stable/c/67bca5f1d644f4e79b694abd8052a177de81c37f
- https://git.kernel.org/stable/c/981f339d2905b6a92ef59358158b326493aecac5
- https://git.kernel.org/stable/c/c6ed54dd90698dc0744d669524cc1c122ded8a16
- https://git.kernel.org/stable/c/c9115f49cf260d24d8b5f2d9a4b63cb31a627bb4
- https://git.kernel.org/stable/c/cc2d2b3dbfb0ba57bc027fb7e1121250c50e4000
- https://git.kernel.org/stable/c/d1308bd0b24cb1d78fa2747d5fa3e055cc628a48
- https://git.kernel.org/stable/c/f748e15253833b771acbede14ea98f50831ac289
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53484.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53484
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
