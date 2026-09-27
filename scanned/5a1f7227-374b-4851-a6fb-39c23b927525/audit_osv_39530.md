# [H] crypto: acomp - fix wrong pointer stored by acomp_save_req()

## Summary
Severity: High
Advisory: CVE-2026-46081
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46081
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: acomp - fix wrong pointer stored by acomp_save_req()

acomp_save_req() stores &req->chain in req->base.data. When
acomp_reqchain_done() is invoked on asynchronous completion, it receives
&req->chain as the data argument but casts it directly to struct
acomp_req. Since data points to the chain member, all subsequent field
accesses are at a wrong offset, resulting in memory corruption.

The issue occurs when an asynchronous hardware implementation, such as
the QAT driver, completes a request that uses the DMA virtual address
interface (e.g. acomp_request_set_src_dma()). This combination causes
crypto_acomp_compress() to enter the acomp_do_req_chain() path, which
sets acomp_reqchain_done() as the completion callback via
acomp_save_req().

With KASAN enabled, this manifests as a general protection fault in
acomp_reqchain_done():

  general protection fault, probably for non-canonical address 0xe000040000000000
  KASAN: probably user-memory-access in range [0x0000400000000000-0x0000400000000007]
  RIP: 0010:acomp_reqchain_done+0x15b/0x4e0
  Call Trace:
   <IRQ>
   qat_comp_alg_callback+0x5d/0xa0 [intel_qat]
   adf_ring_response_handler+0x376/0x8b0 [intel_qat]
   adf_response_handler+0x60/0x170 [intel_qat]
   tasklet_action_common+0x223/0x820
   handle_softirqs+0x1ab/0x640
   </IRQ>

Fix this by storing the request itself in req->base.data instead of
&req->chain, so that acomp_reqchain_done() receives the correct pointer.
Simplify acomp_restore_req() accordingly to access req->chain directly.

## References
- https://git.kernel.org/stable/c/1a2785e5985627f2265ba7775949601a29ba0d1e
- https://git.kernel.org/stable/c/343a5bf68a8ff9affcf2b70677ea4cf40c195ee4
- https://git.kernel.org/stable/c/d7e20b9bd6c990773cf0c09e2642250b8a70263d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46081.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46081
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
