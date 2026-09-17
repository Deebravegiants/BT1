# [H] CVE-2021-3490

## Summary
Severity: High
Advisory: CVE-2021-3490
Aliases: A-190876666, PUB-A-190876666
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-04
Source: https://osv.dev/vulnerability/CVE-2021-3490
Type: osv

## Details
The eBPF ALU32 bounds tracking for bitwise ops (AND, OR and XOR) in the Linux kernel did not properly update 32-bit bounds, which could be turned into out of bounds reads and writes in the Linux kernel and therefore, arbitrary code execution. This issue was fixed via commit 049c4e13714e ("bpf: Fix alu32 const subreg bound tracking on bitwise operations") (v5.13-rc4) and backported to the stable kernels in v5.12.4, v5.11.21, and v5.10.37. The AND/OR issues were introduced by commit 3f50f132d840 ("bpf: Verifier, do explicit ALU32 bounds tracking") (5.7-rc1) and the XOR variant was introduced by 2921c90d4718 ("bpf:Fix a verifier failure with xor") ( 5.10-rc1).

## References
- https://www.zerodayinitiative.com/advisories/ZDI-21-606/
- https://security.netapp.com/advisory/ntap-20210716-0004/
- https://ubuntu.com/security/notices/USN-4949-1
- https://ubuntu.com/security/notices/USN-4950-1
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf.git/commit/?id=049c4e13714ecbca567b4d5f6d563f05d431c80e
- https://www.openwall.com/lists/oss-security/2021/05/11/11
- http://packetstormsecurity.com/files/164015/Linux-eBPF-ALU32-32-bit-Invalid-Bounds-Tracking-Local-Privilege-Escalation.html
