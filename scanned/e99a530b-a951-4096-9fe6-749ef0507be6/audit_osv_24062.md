# [H] misc: fastrpc: fix memory corruption on open

## Summary
Severity: High
Advisory: CVE-2022-49950
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49950
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.213, >=5.5.0 <5.10.142, >=5.11.0 <5.15.66, >=5.16.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: fix memory corruption on open

The probe session-duplication overflow check incremented the session
count also when there were no more available sessions so that memory
beyond the fixed-size slab-allocated session array could be corrupted in
fastrpc_session_alloc() on open().

## References
- https://git.kernel.org/stable/c/5cf2a57c7a01a0d7bdecf875a63682f542891b1b
- https://git.kernel.org/stable/c/cf20c3533efc89578ace94fa20a9e63446223c72
- https://git.kernel.org/stable/c/d245f43aab2b61195d8ebb64cef7b5a08c590ab4
- https://git.kernel.org/stable/c/e0578e603065f120a8759b75e0d6c216c7078a39
- https://git.kernel.org/stable/c/f8632b8bb53ebc005d8f24a68a0c1f9678c0e908
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49950.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49950
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
