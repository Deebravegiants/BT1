# [C] libceph: define and enforce CEPH_MAX_KEY_LEN

## Summary
Severity: Critical
Advisory: CVE-2026-43304
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43304
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

libceph: define and enforce CEPH_MAX_KEY_LEN

When decoding the key, verify that the key material would fit into
a fixed-size buffer in process_auth_done() and generally has a sane
length.

The new CEPH_MAX_KEY_LEN check replaces the existing check for a key
with no key material which is a) not universal since CEPH_CRYPTO_NONE
has to be excluded and b) doesn't provide much value since a smaller
than needed key is just as invalid as no key -- this has to be handled
elsewhere anyway.

## References
- https://git.kernel.org/stable/c/1b275bd49e58752efb83767a5d1aed41356c5e64
- https://git.kernel.org/stable/c/6405e8c680974bb74e2c98d5249fb52c7b12a6c6
- https://git.kernel.org/stable/c/8d745d38c88ecbed95f6b2b39857bf89f35a3244
- https://git.kernel.org/stable/c/ac431d597a9bdfc2ba6b314813f29a6ef2b4a3bf
- https://git.kernel.org/stable/c/c1a0f5f1e5e7e98c36a362ec3d1fcfd9932931ed
- https://git.kernel.org/stable/c/d82467c07b03a27c3c5469b62bb3b726305a80bb
- https://git.kernel.org/stable/c/e1dc45d97975f9db65694d234fbddf1915176e16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43304.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43304
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
