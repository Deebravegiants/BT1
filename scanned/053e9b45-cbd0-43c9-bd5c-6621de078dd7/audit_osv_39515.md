# [H] crypto: authencesn - reject short ahash digests during instance creation

## Summary
Severity: High
Advisory: CVE-2026-46033
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46033
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: authencesn - reject short ahash digests during instance creation

authencesn requires either a zero authsize or an authsize of at least
4 bytes because the ESN encrypt/decrypt paths always move 4 bytes of
high-order sequence number data at the end of the authenticated data.

While crypto_authenc_esn_setauthsize() already rejects explicit
non-zero authsizes in the range 1..3, crypto_authenc_esn_create()
still copied auth->digestsize into inst->alg.maxauthsize without
validating it.  The AEAD core then initialized the tfm's default
authsize from that value.

As a result, selecting an ahash with digest size 1..3, such as
cbcmac(cipher_null), exposed authencesn instances whose default
authsize was invalid even though setauthsize() would have rejected the
same value.  AF_ALG could then trigger the ESN tail handling with a
too-short tag and hit an out-of-bounds access.

Reject authencesn instances whose ahash digest size is in the invalid
non-zero range 1..3 so that no tfm can inherit an unsupported default
authsize.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/2f31cd1e64a079c845bca31d2da7b3c90a311726
- https://git.kernel.org/stable/c/5db6ef9847717329f12c5ea8aba7e9f588a980c0
- https://git.kernel.org/stable/c/67f1f0933cc3d78dde222842bcad2778ec7a0b88
- https://git.kernel.org/stable/c/77f59fb2d3aa33e90ec6cbbf45dcfb20ab82b1a9
- https://git.kernel.org/stable/c/9aff81e8217e9de2929084b03b3c7f81988c112b
- https://git.kernel.org/stable/c/b42821c15445f93daea3e76ada682b2b7181c476
- https://git.kernel.org/stable/c/b69933e97efea238ebbfcf70c2b1be1cd03f13e3
- https://git.kernel.org/stable/c/d4c6a6d08e70bb1083c7c405fc7faacbf19aebc0
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46033.json
- https://access.redhat.com/security/cve/CVE-2026-46033
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46033.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46033
- https://bugzilla.redhat.com/show_bug.cgi?id=2482000
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
