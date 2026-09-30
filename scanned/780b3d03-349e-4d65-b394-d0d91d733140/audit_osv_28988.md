# [H] cppc_cpufreq: Fix possible null pointer dereference

## Summary
Severity: High
Advisory: CVE-2024-38573
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38573
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

cppc_cpufreq: Fix possible null pointer dereference

cppc_cpufreq_get_rate() and hisi_cppc_cpufreq_get_rate() can be called from
different places with various parameters. So cpufreq_cpu_get() can return
null as 'policy' in some circumstances.
Fix this bug by adding null return check.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/769c4f355b7962895205b86ad35617873feef9a5
- https://git.kernel.org/stable/c/9a185cc5a79ba408e1c73375706630662304f618
- https://git.kernel.org/stable/c/b18daa4ec727c0266de5bfc78e818d168cc4aedf
- https://git.kernel.org/stable/c/cf7de25878a1f4508c69dc9f6819c21ba177dbfe
- https://git.kernel.org/stable/c/dfec15222529d22b15e5b0d63572a9e39570cab4
- https://git.kernel.org/stable/c/f84b9b25d045e67a7eee5e73f21278c8ab06713c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38573.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38573
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
