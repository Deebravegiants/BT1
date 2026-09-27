# [H] batman-adv: bla: prevent use-after-free when deleting claims

## Summary
Severity: High
Advisory: CVE-2026-46212
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46212
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: bla: prevent use-after-free when deleting claims

When batadv_bla_del_backbone_claims() removes all claims for a backbone, it
does this by dropping the link entry in the hash list. This list entry
itself was one of the references which need to be dropped at the same time
via batadv_claim_put().

But the batadv_claim_put() must not be done before the last access to the
claim object in this function. Otherwise the claim might be freed already
by the batadv_claim_release() function before the list entry was dropped.

## References
- https://git.kernel.org/stable/c/00155f336a5e8b1006d2ca9ae7ad8fc4a44bb401
- https://git.kernel.org/stable/c/0cc9847c64cb6e61118bc78c9187c8209a7197fa
- https://git.kernel.org/stable/c/1d4b241482d9025c537afb3c7c8419c72c0e0c82
- https://git.kernel.org/stable/c/368449e467d5f1e2c2e987bf2bd57000ba75e10b
- https://git.kernel.org/stable/c/4ae1709a314060a196981b344610d023ea841e57
- https://git.kernel.org/stable/c/6c5dc6d68e6ba7f0224a757a39ed52fcdb54d472
- https://git.kernel.org/stable/c/a1a99837bb6169cfb9187abaa2005e8f12079426
- https://git.kernel.org/stable/c/b88c865dcf6e9f20bfe66a360d4b62941ef769b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46212.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46212
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
