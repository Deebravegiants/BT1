# [H] x86/cpu: Avoid running off the end of an AMD erratum table

## Summary
Severity: High
Advisory: CVE-2025-37751
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-37751
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/cpu: Avoid running off the end of an AMD erratum table

The NULL array terminator at the end of erratum_1386_microcode was
removed during the switch from x86_cpu_desc to x86_cpu_id. This
causes readers to run off the end of the array.

Replace the NULL.

## References
- https://git.kernel.org/stable/c/1b518f73f1b6f59e083ec33dea22d9a1a275a970
- https://git.kernel.org/stable/c/f0df00ebc57f803603f2a2e0df197e51f06fbe90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37751.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37751
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
