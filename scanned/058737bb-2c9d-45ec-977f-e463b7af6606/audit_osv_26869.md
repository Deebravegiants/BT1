# [C] net/smc: fix potential panic dues to unprotected smc_llc_srv_add_link()

## Summary
Severity: Critical
Advisory: CVE-2023-54237
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54237
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.8.0 <6.1.16, >=6.2.0 <6.2.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: fix potential panic dues to unprotected smc_llc_srv_add_link()

There is a certain chance to trigger the following panic:

PID: 5900   TASK: ffff88c1c8af4100  CPU: 1   COMMAND: "kworker/1:48"
 #0 [ffff9456c1cc79a0] machine_kexec at ffffffff870665b7
 #1 [ffff9456c1cc79f0] __crash_kexec at ffffffff871b4c7a
 #2 [ffff9456c1cc7ab0] crash_kexec at ffffffff871b5b60
 #3 [ffff9456c1cc7ac0] oops_end at ffffffff87026ce7
 #4 [ffff9456c1cc7ae0] page_fault_oops at ffffffff87075715
 #5 [ffff9456c1cc7b58] exc_page_fault at ffffffff87ad0654
 #6 [ffff9456c1cc7b80] asm_exc_page_fault at ffffffff87c00b62
    [exception RIP: ib_alloc_mr+19]
    RIP: ffffffffc0c9cce3  RSP: ffff9456c1cc7c38  RFLAGS: 00010202
    RAX: 0000000000000000  RBX: 0000000000000002  RCX: 0000000000000004
    RDX: 0000000000000010  RSI: 0000000000000000  RDI: 0000000000000000
    RBP: ffff88c1ea281d00   R8: 000000020a34ffff   R9: ffff88c1350bbb20
    R10: 0000000000000000  R11: 0000000000000001  R12: 0000000000000000
    R13: 0000000000000010  R14: ffff88c1ab040a50  R15: ffff88c1ea281d00
    ORIG_RAX: ffffffffffffffff  CS: 0010  SS: 0018
 #7 [ffff9456c1cc7c60] smc_ib_get_memory_region at ffffffffc0aff6df [smc]
 #8 [ffff9456c1cc7c88] smcr_buf_map_link at ffffffffc0b0278c [smc]
 #9 [ffff9456c1cc7ce0] __smc_buf_create at ffffffffc0b03586 [smc]

The reason here is that when the server tries to create a second link,
smc_llc_srv_add_link() has no protection and may add a new link to
link group. This breaks the security environment protected by
llc_conf_mutex.

## References
- https://git.kernel.org/stable/c/0c764cc271d3aa6528ae1b3394babf34ac01f775
- https://git.kernel.org/stable/c/e40b801b3603a8f90b46acbacdea3505c27f01c0
- https://git.kernel.org/stable/c/f2f46de98c11d41ac8d22765f47ba54ce5480a5b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54237.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54237
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
