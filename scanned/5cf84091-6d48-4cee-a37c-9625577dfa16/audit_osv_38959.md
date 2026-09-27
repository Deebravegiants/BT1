# [H] netfilter: xt_tcpmss: check remaining length before reading optlen

## Summary
Severity: High
Advisory: CVE-2026-43190
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43190
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: xt_tcpmss: check remaining length before reading optlen

Quoting reporter:
  In net/netfilter/xt_tcpmss.c (lines 53-68), the TCP option parser reads
 op[i+1] directly without validating the remaining option length.

  If the last byte of the option field is not EOL/NOP (0/1), the code attempts
  to index op[i+1]. In the case where i + 1 == optlen, this causes an
  out-of-bounds read, accessing memory past the optlen boundary
  (either reading beyond the stack buffer _opt or the
  following payload).

## References
- https://git.kernel.org/stable/c/07a9b32eaae792ff7d0fcac14d8920c937c0a9c3
- https://git.kernel.org/stable/c/5e13d0a37666955b6cfddc0f73cb40ed645b8a05
- https://git.kernel.org/stable/c/735ee8582da3d239eb0c7a53adca61b79fb228b3
- https://git.kernel.org/stable/c/8b300f726640c48c3edfe9c453334dd801f4b74e
- https://git.kernel.org/stable/c/cd5beda7e0e32865e214f28034bb92c1cecff885
- https://git.kernel.org/stable/c/eaedc0bc18be46fe7f58170e967959a932c4f824
- https://git.kernel.org/stable/c/f6c412dcfd76b0516d51aa847d8f4c7b70381b09
- https://git.kernel.org/stable/c/f895191dc32c53eaf443b6443fe40945b2f92287
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43190.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43190
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
