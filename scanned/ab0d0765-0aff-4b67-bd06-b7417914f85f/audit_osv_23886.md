# [M] cpufreq: pmac32-cpufreq: Fix refcount leak bug

## Summary
Severity: Medium
Advisory: CVE-2022-49621
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49621
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.324, >=4.10.0 <4.14.289, >=4.15.0 <4.19.253, >=4.20.0 <5.4.207, >=5.5.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

cpufreq: pmac32-cpufreq: Fix refcount leak bug

In pmac_cpufreq_init_MacRISC3(), we need to add corresponding
of_node_put() for the three node pointers whose refcount have
been incremented by of_find_node_by_name().

## References
- https://git.kernel.org/stable/c/37c16fc2cb13a13f3c0193bfc6f2edef7d7df7d7
- https://git.kernel.org/stable/c/3ea9dbf7c2f436952bca331c6f5d72f75aca224e
- https://git.kernel.org/stable/c/4513018d0bd739097570d26a7760551cba3deb56
- https://git.kernel.org/stable/c/4585890ab2dbf455d80e254d3d859d4c1e357920
- https://git.kernel.org/stable/c/4f242486bf46d314b2e3838cc64b56f008a3c4d7
- https://git.kernel.org/stable/c/57289b6601fe78c09921599b042a0b430fb420ec
- https://git.kernel.org/stable/c/8dda30f81c751b01cd71f2cfaeef26ad4393b1d1
- https://git.kernel.org/stable/c/ccd7567d4b6cf187fdfa55f003a9e461ee629e36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49621.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49621
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
