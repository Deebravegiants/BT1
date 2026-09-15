# [H] NFSD: Avoid calling OPDESC() with ops->opnum == OP_ILLEGAL

## Summary
Severity: High
Advisory: CVE-2023-53680
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53680
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.220, >=5.11.0 <5.15.107, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFSD: Avoid calling OPDESC() with ops->opnum == OP_ILLEGAL

OPDESC() simply indexes into nfsd4_ops[] by the op's operation
number, without range checking that value. It assumes callers are
careful to avoid calling it with an out-of-bounds opnum value.

nfsd4_decode_compound() is not so careful, and can invoke OPDESC()
with opnum set to OP_ILLEGAL, which is 10044 -- well beyond the end
of nfsd4_ops[].

## References
- https://git.kernel.org/stable/c/50827896c365e0f6c8b55ed56d444dafd87c92c5
- https://git.kernel.org/stable/c/804d8e0a6e54427268790472781e03bc243f4ee3
- https://git.kernel.org/stable/c/a64160124d5a078be0c380b1e8a0bad2d040d3a1
- https://git.kernel.org/stable/c/f352c41fa718482979e7e6b71b4da2b718e381cc
- https://git.kernel.org/stable/c/ffcbcf087581ae68ddc0a21460f7ecd4315bdd0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53680.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53680
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
