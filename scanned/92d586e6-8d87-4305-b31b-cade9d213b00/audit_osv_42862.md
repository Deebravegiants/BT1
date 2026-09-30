# [C] espintcp: use sk_msg_free_partial to fix partial send

## Summary
Severity: Critical
Advisory: CVE-2026-72041
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72041
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

espintcp: use sk_msg_free_partial to fix partial send

sk_msg_free_partial() ensures consistency of the skmsg at every
iteration, without having to manually handle uncharges and offsets.
This simplifies the code, and fixes some bugs in skmsg accounting when
we don't send the full contents.

## References
- https://git.kernel.org/stable/c/007800408002d871f5699bdb944f985896730b8f
- https://git.kernel.org/stable/c/14c0b42c8a2cd9b5361bbff45b52f69c62c6a286
- https://git.kernel.org/stable/c/4ea8c051b4bd7feec7749a980f2f70e1782b84d7
- https://git.kernel.org/stable/c/518dcb84b997dff461800b079e5f2596389f766a
- https://git.kernel.org/stable/c/54d73f18f8919735f4d04d6f43374f75756c0180
- https://git.kernel.org/stable/c/a338ce41bc933d8f74c39d9b3b6f1d8ca53d9714
- https://git.kernel.org/stable/c/a66d45e0ce6d73cd79962d422388e61bfaf0cb50
- https://git.kernel.org/stable/c/a977f78adce40b39d90d9567e7987bb110102810
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72041.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72041
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
