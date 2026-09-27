# [H] lib/crypto: chacha: Zeroize permuted_state before it leaves scope

## Summary
Severity: High
Advisory: CVE-2026-43336
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43336
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

lib/crypto: chacha: Zeroize permuted_state before it leaves scope

Since the ChaCha permutation is invertible, the local variable
'permuted_state' is sufficient to compute the original 'state', and thus
the key, even after the permutation has been done.

While the kernel is quite inconsistent about zeroizing secrets on the
stack (and some prominent userspace crypto libraries don't bother at all
since it's not guaranteed to work anyway), the kernel does try to do it
as a best practice, especially in cases involving the RNG.

Thus, explicitly zeroize 'permuted_state' before it goes out of scope.

## References
- https://git.kernel.org/stable/c/066c760acead1fb743bae294dbd89f479ae43b9b
- https://git.kernel.org/stable/c/1933249263c3a98df79992f61a566476e4163bcc
- https://git.kernel.org/stable/c/1d761e5a7340c46479fb2399598f331e4fe2c633
- https://git.kernel.org/stable/c/91999af43ca2125e3b2c18fcfc02912ada02efc3
- https://git.kernel.org/stable/c/b416a4245f04a450c67a13e6d96056c37c5b33fe
- https://git.kernel.org/stable/c/bd62d9b44464a6c20a34a74068e7a784d0afa04a
- https://git.kernel.org/stable/c/e5046823f8fa3677341b541a25af2fcb99a5b1e0
- https://git.kernel.org/stable/c/e90ee961af515a484f091678ce58a4c3f7b73b02
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43336.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43336
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
