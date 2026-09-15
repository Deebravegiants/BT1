# [M] mptcp: really cope with fastopen race

## Summary
Severity: Medium
Advisory: CVE-2024-26708
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26708
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.18, >=6.7.0 <6.7.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: really cope with fastopen race

Fastopen and PM-trigger subflow shutdown can race, as reported by
syzkaller.

In my first attempt to close such race, I missed the fact that
the subflow status can change again before the subflow_state_change
callback is invoked.

Address the issue additionally copying with all the states directly
reachable from TCP_FIN_WAIT1.

## References
- https://git.kernel.org/stable/c/337cebbd850f94147cee05252778f8f78b8c337f
- https://git.kernel.org/stable/c/4bfe217e075d04e63c092df9d40c608e598c2ef2
- https://git.kernel.org/stable/c/e158fb9679d15a2317ec13b4f6301bd26265df2f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26708.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26708
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
