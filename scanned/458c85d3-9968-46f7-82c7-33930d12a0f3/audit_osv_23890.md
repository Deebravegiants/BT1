# [M] ima: Fix potential memory leak in ima_init_crypto()

## Summary
Severity: Medium
Advisory: CVE-2022-49627
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49627
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.132, >=5.11.0 <5.15.56, >=5.16.0 <5.18.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ima: Fix potential memory leak in ima_init_crypto()

On failure to allocate the SHA1 tfm, IMA fails to initialize and exits
without freeing the ima_algo_array. Add the missing kfree() for
ima_algo_array to avoid the potential memory leak.

## References
- https://git.kernel.org/stable/c/067d2521874135267e681c19d42761c601d503d6
- https://git.kernel.org/stable/c/601ae26aa2802a4c10c94d7388a99eabdbefab2b
- https://git.kernel.org/stable/c/830de9667b3ada0a75a3f098dfc7159709fe397b
- https://git.kernel.org/stable/c/c1d9702ceb4a091da6bee380627596d1fba09274
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49627.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49627
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
