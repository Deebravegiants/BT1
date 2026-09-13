# [H] ksmbd: fix slab-out-of-bounds in smb2_allocate_rsp_buf

## Summary
Severity: High
Advisory: CVE-2024-26980
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-26980
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.159, >=5.16.0 <6.1.88, >=6.2.0 <6.6.29, >=6.7.0 <6.8.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix slab-out-of-bounds in smb2_allocate_rsp_buf

If ->ProtocolId is SMB2_TRANSFORM_PROTO_NUM, smb2 request size
validation could be skipped. if request size is smaller than
sizeof(struct smb2_query_info_req), slab-out-of-bounds read can happen in
smb2_allocate_rsp_buf(). This patch allocate response buffer after
decrypting transform request. smb3_decrypt_req() will validate transform
request size and avoid slab-out-of-bound in smb2_allocate_rsp_buf().

## References
- https://git.kernel.org/stable/c/0977f89722eceba165700ea384f075143f012085
- https://git.kernel.org/stable/c/3160d9734453a40db248487f8204830879c207f1
- https://git.kernel.org/stable/c/b80ba648714e6d790d69610cf14656be222d0248
- https://git.kernel.org/stable/c/c119f4ede3fa90a9463f50831761c28f989bfb20
- https://git.kernel.org/stable/c/da21401372607c49972ea87a6edaafb36a17c325
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4EZ6PJW7VOZ224TD7N4JZNU6KV32ZJ53/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DAMSOZXJEPUOXW33WZYWCVAY7Z5S7OOY/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GCBZZEC7L7KTWWAS2NLJK6SO3IZIL4WW/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26980.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26980
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
