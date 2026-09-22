# [H] perf: Revert to requiring CAP_SYS_ADMIN for uprobes

## Summary
Severity: High
Advisory: CVE-2025-38466
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38466
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <5.10.240, >=5.11.0 <5.15.189, >=5.16.0 <6.1.146, >=6.2.0 <6.6.99, >=6.7.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf: Revert to requiring CAP_SYS_ADMIN for uprobes

Jann reports that uprobes can be used destructively when used in the
middle of an instruction. The kernel only verifies there is a valid
instruction at the requested offset, but due to variable instruction
length cannot determine if this is an instruction as seen by the
intended execution stream.

Additionally, Mark Rutland notes that on architectures that mix data
in the text segment (like arm64), a similar things can be done if the
data word is 'mistaken' for an instruction.

As such, require CAP_SYS_ADMIN for uprobes.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/183bdb89af1b5193b1d1d9316986053b15ca6fa4
- https://git.kernel.org/stable/c/8e8bf7bc6aa6f583336c2fda280b6cea0aed5612
- https://git.kernel.org/stable/c/a0a8009083e569b5526c64f7d3f2a62baca95164
- https://git.kernel.org/stable/c/ba677dbe77af5ffe6204e0f3f547f3ba059c6302
- https://git.kernel.org/stable/c/c0aec35f861fa746ca45aa816161c74352e6ada8
- https://git.kernel.org/stable/c/d5074256b642cdeb46a70ce2f15193e766edca68
- https://git.kernel.org/stable/c/d7ef1afd5b3f43f4924326164cee5397b66abd9c
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38466.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38466
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
