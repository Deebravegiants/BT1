# [H] s390/zcrypt: Fix buffer over-read in cca_cipher2protkey

## Summary
Severity: High
Advisory: CVE-2026-68453
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-68453
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/zcrypt: Fix buffer over-read in cca_cipher2protkey

Add validation of both the actual key buffer size and token length
fields in all the cca_check_sec*token() functions. Additionally check
in cca_gencipherkey() for possible underflow with returned key size.

The CCA token structures contain user-controlled len fields that
were used in operations without proper validation against both the
actual buffer size and minimum token structure size. An attacker
could set this field larger than the actual buffer size, leading to
reading beyond buffer boundaries. This may result in a kernel crash or
exposure of memory via sending this as part of a request down to the
crypto card. Also an attacker could have used a very small len value
and thus enforce a buffer under-run which may produce similar effects
as a over-read.

So now a key must
- key buf length must be at least sizeof the token struct
- the key len field inside the token must fit into the range of
  sizeof key token struct ... key buf length

## References
- https://git.kernel.org/stable/c/36b230835b8a008266aad22168ca52afacc8a58d
- https://git.kernel.org/stable/c/3b2abee2a678607ae27975bc6833785c2002df43
- https://git.kernel.org/stable/c/a57fd7fcdb63e2d5ceac78bbe825ec986062a9da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68453.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68453
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
