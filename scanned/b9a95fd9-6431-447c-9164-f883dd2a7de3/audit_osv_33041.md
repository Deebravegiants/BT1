# [H] bpf: handle jset (if a & b ...) as a jump in CFG computation

## Summary
Severity: High
Advisory: CVE-2025-38607
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-19
Source: https://osv.dev/vulnerability/CVE-2025-38607
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.10, >=6.16.0 <6.16.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: handle jset (if a & b ...) as a jump in CFG computation

BPF_JSET is a conditional jump and currently verifier.c:can_jump()
does not know about that. This can lead to incorrect live registers
and SCC computation.

E.g. in the following example:

   1: r0 = 1;
   2: r2 = 2;
   3: if r1 & 0x7 goto +1;
   4: exit;
   5: r0 = r2;
   6: exit;

W/o this fix insn_successors(3) will return only (4), a jump to (5)
would be missed and r2 won't be marked as alive at (3).

## References
- https://git.kernel.org/stable/c/261b30ad1516f4b9edd500aa6e8d6315c8fc109a
- https://git.kernel.org/stable/c/3157f7e2999616ac91f4d559a8566214f74000a5
- https://git.kernel.org/stable/c/65eb166b8636365ad3d6e36d50a7c5edfe6cc66e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38607.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38607
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
