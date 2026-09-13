# [C] netfilter: nf_conntrack_h323: check for zero length in DecodeQ931()

## Summary
Severity: Critical
Advisory: CVE-2026-23455
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23455
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.17 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_h323: check for zero length in DecodeQ931()

In DecodeQ931(), the UserUserIE code path reads a 16-bit length from
the packet, then decrements it by 1 to skip the protocol discriminator
byte before passing it to DecodeH323_UserInformation(). If the encoded
length is 0, the decrement wraps to -1, which is then passed as a
large value to the decoder, leading to an out-of-bounds read.

Add a check to ensure len is positive after the decrement.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/2121f5fbe88daff0f1fc5bc47d359426c74b86b0
- https://git.kernel.org/stable/c/495e97af9e7249ee02b72bb1d0848a6efc3700f4
- https://git.kernel.org/stable/c/633e8f87dad32263f6a57dccdb873f042c062111
- https://git.kernel.org/stable/c/65fa92f79677858b14b9e4b7275f26639afe2710
- https://git.kernel.org/stable/c/9d00fe7d6d7c5b5f1065a6e042b54f2e44bd6df8
- https://git.kernel.org/stable/c/b652b05d51003ac074b912684f9ec7486231717b
- https://git.kernel.org/stable/c/f173d0f4c0f689173f8cdac79991043a4a89bf66
- https://git.kernel.org/stable/c/f5e4f4e4cdb75ec36802059a94195a31f193da60
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23455.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23455
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
