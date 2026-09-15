# [H] proc: protect ptrace_may_access() with exec_update_lock (FD links)

## Summary
Severity: High
Advisory: CVE-2026-64375
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64375
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.18 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

proc: protect ptrace_may_access() with exec_update_lock (FD links)

proc_pid_get_link() and proc_pid_readlink() currently look up the task from
the pid once, then do the ptrace access check on that task, then look up
the task from the pid a second time to do the actual access.
That's racy in several ways.

To fix it, pass the task to the ->proc_get_link() handler, and instead of
proc_fd_access_allowed(), introduce a new helper call_proc_get_link() that
looks up and locks the task, does the access check, and calls
->proc_get_link().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/138c692d2b2d63d26f2eb957d0e4fcc5d61f9ff2
- https://git.kernel.org/stable/c/497c6bae5167428596575f20af6613ff5671f383
- https://git.kernel.org/stable/c/6253dfee5afba536bb54fc6fe6c091c3758fafe1
- https://git.kernel.org/stable/c/6255da28d4bb5349fe18e84cb043ccd394eba75d
- https://git.kernel.org/stable/c/65bf0d2b6e914f1448d6a2fde193dcf60936a651
- https://git.kernel.org/stable/c/83b17872e3166c295c599279fc9562ac3840c638
- https://git.kernel.org/stable/c/de497d7aa2fae453a7e7c8f7d3e8682e565e3aaf
- https://git.kernel.org/stable/c/dfd1894cb64cbd8758b461ed713800fe73db4f82
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64375.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64375
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
