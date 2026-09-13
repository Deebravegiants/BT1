# [H] tracing: fprobe events: Fix possible UAF on modules

## Summary
Severity: High
Advisory: CVE-2025-37845
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37845
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: fprobe events: Fix possible UAF on modules

Commit ac91052f0ae5 ("tracing: tprobe-events: Fix leakage of module
refcount") moved try_module_get() from __find_tracepoint_module_cb()
to find_tracepoint() caller, but that introduced a possible UAF
because the module can be unloaded before try_module_get(). In this
case, the module object should be freed too. Thus, try_module_get()
does not only fail but may access to the freed object.

To avoid that, try_module_get() in __find_tracepoint_module_cb()
again.

## References
- https://git.kernel.org/stable/c/626f01f4d26e8cf92e69c1df53036153c8e98a20
- https://git.kernel.org/stable/c/868df4eb784c3ccc7e4340a9ea993cbbedca167e
- https://git.kernel.org/stable/c/a27d2de2472b1cc7d582ab405d1d5832a80481de
- https://git.kernel.org/stable/c/dd941507a9486252d6fcf11814387666792020f3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37845.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37845
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
