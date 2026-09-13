# [H] crypto: af_alg - Fix page reassignment overflow in af_alg_pull_tsgl

## Summary
Severity: High
Advisory: CVE-2026-43078
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43078
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.254, >=5.11.0 <5.15.204, >=5.16.0 <6.1.170, >=6.2.0 <6.6.137, >=6.7.0 <6.12.85, >=6.13.0 <6.18.24, >=6.19.0 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: af_alg - Fix page reassignment overflow in af_alg_pull_tsgl

When page reassignment was added to af_alg_pull_tsgl the original
loop wasn't updated so it may try to reassign one more page than
necessary.

Add the check to the reassignment so that this does not happen.

Also update the comment which still refers to the obsolete offset
argument.

## References
- https://git.kernel.org/stable/c/2b781d1d4f933990318bcc5c68fb75a717379e42
- https://git.kernel.org/stable/c/31d00156e50ecad37f2cb6cbf04aaa9a260505ef
- https://git.kernel.org/stable/c/710a4ce5d7afd9fe082c75dec282ab4a11c0fe71
- https://git.kernel.org/stable/c/9532501e0f1b200ea80baa0e33e0b06da10bb271
- https://git.kernel.org/stable/c/c8369a6d62f5abde9cbd4b62c45bf4b996be2468
- https://git.kernel.org/stable/c/dea5fcf085f977b6c2de1b2d4ec4767b6c840d1f
- https://git.kernel.org/stable/c/f7826bc0b39928a4a22f6b815dd9940b22a63503
- https://git.kernel.org/stable/c/fa48d3ea9cdbfb28c1fd6756c6c5cd01351aa51e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43078.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
