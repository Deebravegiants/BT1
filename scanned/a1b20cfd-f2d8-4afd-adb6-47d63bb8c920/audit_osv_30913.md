# [H] x86/CPU/AMD: Terminate the erratum_1386_microcode array

## Summary
Severity: High
Advisory: CVE-2024-56721
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-12-29
Source: https://osv.dev/vulnerability/CVE-2024-56721
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/CPU/AMD: Terminate the erratum_1386_microcode array

The erratum_1386_microcode array requires an empty entry at the end.
Otherwise x86_match_cpu_with_stepping() will continue iterate the array after
it ended.

Add an empty entry to erratum_1386_microcode to its end.

## References
- https://git.kernel.org/stable/c/82d6b82cf89d950982ac240ba068c3a7e1f23b0a
- https://git.kernel.org/stable/c/ccfee14f08b8699132b87bc6d78e0fa75bf094dd
- https://git.kernel.org/stable/c/ff6cdc407f4179748f4673c39b0921503199a0ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56721.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56721
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
