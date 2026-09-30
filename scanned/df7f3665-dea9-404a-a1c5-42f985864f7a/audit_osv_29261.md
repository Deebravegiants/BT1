# [C] ila: block BH in ila_output()

## Summary
Severity: Critical
Advisory: CVE-2024-41081
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41081
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.319, >=4.20.0 <5.4.281, >=5.5.0 <5.10.223, >=5.11.0 <5.15.164, >=5.16.0 <6.1.101, >=6.2.0 <6.6.42, >=6.7.0 <6.9.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ila: block BH in ila_output()

As explained in commit 1378817486d6 ("tipc: block BH
before using dst_cache"), net/core/dst_cache.c
helpers need to be called with BH disabled.

ila_output() is called from lwtunnel_output()
possibly from process context, and under rcu_read_lock().

We might be interrupted by a softirq, re-enter ila_output()
and corrupt dst_cache data structures.

Fix the race by using local_bh_disable().

## References
- https://git.kernel.org/stable/c/522c3336c2025818fa05e9daf0ac35711e55e316
- https://git.kernel.org/stable/c/7435bd2f84a25aba607030237261b3795ba782da
- https://git.kernel.org/stable/c/96103371091c6476eb07f4c66624bdd1b42f758a
- https://git.kernel.org/stable/c/9f9c79d8e527d867e0875868b14fb76e6011e70c
- https://git.kernel.org/stable/c/a0cafb7b0b94d18e4813ee4b712a056f280e7b5a
- https://git.kernel.org/stable/c/b4eb25a3d70df925a9fa4e82d17a958a0a228f5f
- https://git.kernel.org/stable/c/cf28ff8e4c02e1ffa850755288ac954b6ff0db8c
- https://git.kernel.org/stable/c/feac2391e26b086f73be30e9b1ab215eada8d830
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41081.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41081
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
