# [H] cifs: fix oops during encryption

## Summary
Severity: High
Advisory: CVE-2022-50341
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2022-50341
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.16, >=6.1.0 <6.1.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

cifs: fix oops during encryption

When running xfstests against Azure the following oops occurred on an
arm64 system

  Unable to handle kernel write to read-only memory at virtual address
  ffff0001221cf000
  Mem abort info:
    ESR = 0x9600004f
    EC = 0x25: DABT (current EL), IL = 32 bits
    SET = 0, FnV = 0
    EA = 0, S1PTW = 0
    FSC = 0x0f: level 3 permission fault
  Data abort info:
    ISV = 0, ISS = 0x0000004f
    CM = 0, WnR = 1
  swapper pgtable: 4k pages, 48-bit VAs, pgdp=00000000294f3000
  [ffff0001221cf000] pgd=18000001ffff8003, p4d=18000001ffff8003,
  pud=18000001ff82e003, pmd=18000001ff71d003, pte=00600001221cf787
  Internal error: Oops: 9600004f [#1] PREEMPT SMP
  ...
  pstate: 80000005 (Nzcv daif -PAN -UAO -TCO BTYPE=--)
  pc : __memcpy+0x40/0x230
  lr : scatterwalk_copychunks+0xe0/0x200
  sp : ffff800014e92de0
  x29: ffff800014e92de0 x28: ffff000114f9de80 x27: 0000000000000008
  x26: 0000000000000008 x25: ffff800014e92e78 x24: 0000000000000008
  x23: 0000000000000001 x22: 0000040000000000 x21: ffff000000000000
  x20: 0000000000000001 x19: ffff0001037c4488 x18: 0000000000000014
  x17: 235e1c0d6efa9661 x16: a435f9576b6edd6c x15: 0000000000000058
  x14: 0000000000000001 x13: 0000000000000008 x12: ffff000114f2e590
  x11: ffffffffffffffff x10: 0000040000000000 x9 : ffff8000105c3580
  x8 : 2e9413b10000001a x7 : 534b4410fb86b005 x6 : 534b4410fb86b005
  x5 : ffff0001221cf008 x4 : ffff0001037c4490 x3 : 0000000000000001
  x2 : 0000000000000008 x1 : ffff0001037c4488 x0 : ffff0001221cf000
  Call trace:
   __memcpy+0x40/0x230
   scatterwalk_map_and_copy+0x98/0x100
   crypto_ccm_encrypt+0x150/0x180
   crypto_aead_encrypt+0x2c/0x40
   crypt_message+0x750/0x880
   smb3_init_transform_rq+0x298/0x340
   smb_send_rqst.part.11+0xd8/0x180
   smb_send_rqst+0x3c/0x100
   compound_send_recv+0x534/0xbc0
   smb2_query_info_compound+0x32c/0x440
   smb2_set_ea+0x438/0x4c0
   cifs_xattr_set+0x5d4/0x7c0

This is because in scatterwalk_copychunks(), we attempted to write to
a buffer (@sign) that was allocated in the stack (vmalloc area) by
crypt_message() and thus accessing its remaining 8 (x2) bytes ended up
crossing a page boundary.

To simply fix it, we could just pass @sign kmalloc'd from
crypt_message() and then we're done.  Luckily, we don't seem to pass
any other vmalloc'd buffers in smb_rqst::rq_iov...

Instead, let's map the correct pages and offsets from vmalloc buffers
as well in cifs_sg_set_buf() and then avoiding such oopses.

## References
- https://git.kernel.org/stable/c/a13e51760703f71c25d5fc1f4a62dfa4b0cc80e9
- https://git.kernel.org/stable/c/bf0543b93740916ee91956f9a63da6fc0d79daaa
- https://git.kernel.org/stable/c/e8d16a54842d609fd4a3ed2d81d4333d6329aa94
- https://git.kernel.org/stable/c/e8e2861cc3258dbe407d01ea8c59bb5a53132301
- https://git.kernel.org/stable/c/f7f291e14dde32a07b1f0aa06921d28f875a7b54
- https://git.kernel.org/stable/c/fe6ea044c4f05706cb71040055b1c70c6c8275e0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50341.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50341
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
