# [H] CVE-2021-3489

## Summary
Severity: High
Advisory: CVE-2021-3489
Aliases: A-190877279, PUB-A-190877279
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-04
Source: https://osv.dev/vulnerability/CVE-2021-3489
Type: osv

## Details
The eBPF RINGBUF bpf_ringbuf_reserve() function in the Linux kernel did not check that the allocated size was smaller than the ringbuf size, allowing an attacker to perform out-of-bounds writes within the kernel and therefore, arbitrary code execution. This issue was fixed via commit 4b81ccebaeee ("bpf, ringbuf: Deny reserve of buffers larger than ringbuf") (v5.13-rc4) and backported to the stable kernels in v5.12.4, v5.11.21, and v5.10.37. It was introduced via 457f44363a88 ("bpf: Implement BPF ring buffer and verifier support for it") (v5.8-rc1).

## References
- https://www.zerodayinitiative.com/advisories/ZDI-21-590/
- https://security.netapp.com/advisory/ntap-20210716-0004/
- https://ubuntu.com/security/notices/USN-4949-1
- https://ubuntu.com/security/notices/USN-4950-1
- https://www.openwall.com/lists/oss-security/2021/05/11/10
- https://git.kernel.org/pub/scm/linux/kernel/git/bpf/bpf.git/commit/?id=4b81ccebaeee885ab1aa1438133f2991e3a2b6ea
