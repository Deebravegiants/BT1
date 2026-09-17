# [H] NFSv4/flexfiles: reject zero filehandle version count

## Summary
Severity: High
Advisory: CVE-2026-53392
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-53392
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.0.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSv4/flexfiles: reject zero filehandle version count

ff_layout_alloc_lseg() decodes the filehandle-version array count
from the flexfiles layout body. The value is used as the count for
kzalloc_objs(), and the current code only rejects NULL.

A zero count yields ZERO_SIZE_PTR, which can be stored in
dss_info->fh_versions even though later flexfiles paths assume that at
least one filehandle version exists.

Reject fh_count == 0 before the allocation, matching the existing zero
version_count validation in the flexfiles GETDEVICEINFO parser.

A QEMU/KASAN run with a malformed flexfiles layout hit:

  KASAN: null-ptr-deref in range [0x0000000000000010-0x0000000000000017]
  RIP: 0010:ff_layout_encode_ff_layoutupdate.isra.0+0x15f/0x750
  ff_layout_encode_layoutreturn+0x683/0x970
  nfs4_xdr_enc_layoutreturn+0x278/0x3a0
  Kernel panic - not syncing: Fatal exception

The patched kernel rejects the malformed layout without KASAN/oops/panic,
and a valid fh_count=1 regression still opens, reads, and unmounts cleanly.

## References
- https://git.kernel.org/stable/c/18cc6d57a14fa65ab2a2b52279f549041c4bc9cf
- https://git.kernel.org/stable/c/2131ed64b767ffa8bcdb3677d90f3964e39aabc8
- https://git.kernel.org/stable/c/2c6bb3c40bc24f6aa8dfbe6fe98c3ad6389203f2
- https://git.kernel.org/stable/c/7779c85028a0676fb190cde4f0c540f4f8e97761
- https://git.kernel.org/stable/c/9033591535c066726f5b505126ccb4068b98fa4f
- https://git.kernel.org/stable/c/be7829715e341b42846437dd9e721005db59f0cc
- https://git.kernel.org/stable/c/d8c90c7cc061265d5f2813a1f5c82ef2f4707e67
- https://git.kernel.org/stable/c/eeabb9020721db6bc132e68eeae380b8d4fb4b04
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53392.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53392
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
