# [M] cpufreq: CPPC: Fix possible null-ptr-deref for cppc_get_cpu_cost()

## Summary
Severity: Medium
Advisory: CVE-2024-53230
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53230
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

cpufreq: CPPC: Fix possible null-ptr-deref for cppc_get_cpu_cost()

cpufreq_cpu_get_raw() may return NULL if the cpu is not in
policy->cpus cpu mask and it will cause null pointer dereference,
so check NULL for cppc_get_cpu_cost().

## References
- https://git.kernel.org/stable/c/1975b481f644f8f841d9c188e3c214fce187f18b
- https://git.kernel.org/stable/c/1a1374bb8c5926674973d849feed500bc61ad535
- https://git.kernel.org/stable/c/6be57617a38b3f33266acecdb3c063c1c079aaf7
- https://git.kernel.org/stable/c/afd22d9839359829776abb55cc9bc4946e888704
- https://git.kernel.org/stable/c/f05ef81db63889f6f14eb77fd140dac6cedb6f7f
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53230.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53230
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
