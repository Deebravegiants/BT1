# [H] crypto: algif_hash - fix double free in hash_accept

## Summary
Severity: High
Advisory: CVE-2025-38079
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2025-38079
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.38 <5.4.294, >=5.5.0 <5.10.238, >=5.11.0 <5.15.185, >=5.16.0 <6.1.141, >=6.2.0 <6.6.93, >=6.7.0 <6.12.31, >=6.13.0 <6.14.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: algif_hash - fix double free in hash_accept

If accept(2) is called on socket type algif_hash with
MSG_MORE flag set and crypto_ahash_import fails,
sk2 is freed. However, it is also freed in af_alg_release,
leading to slab-use-after-free error.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/0346f4b742345d1c733c977f3a7aef5a6419a967
- https://git.kernel.org/stable/c/134daaba93193df9e988524b5cd2f52d15eb1993
- https://git.kernel.org/stable/c/2f45a8d64fb4ed4830a4b3273834ecd6ca504896
- https://git.kernel.org/stable/c/5bff312b59b3f2a54ff504e4f4e47272b64f3633
- https://git.kernel.org/stable/c/b2df03ed4052e97126267e8c13ad4204ea6ba9b6
- https://git.kernel.org/stable/c/bf7bba75b91539e93615f560893a599c1e1c98bf
- https://git.kernel.org/stable/c/c3059d58f79fdfb2201249c2741514e34562b547
- https://git.kernel.org/stable/c/f0f3d09f53534ea385d55ced408f2b67059b16e4
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38079.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38079
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
