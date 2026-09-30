# [H] keys: Pin request_key_auth payload in instantiate paths

## Summary
Severity: High
Advisory: CVE-2026-63823
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63823
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.16 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

keys: Pin request_key_auth payload in instantiate paths

A: request_key()       B: KEYCTL_INSTANTIATE_IOV
================       =========================

create auth key
store rka in auth key
wait for helper
                       get auth key
                       load rka from auth key
                       copy user payload
                       sleep on #PF

helper completed
detach and free rka
destroy auth key
                       wake up
                       use rka->target_key
                       **USE-AFTER-FREE**

Give request_key_auth payloads a refcount.  Take a payload reference while
authkey->sem stabilizes the payload and revocation state.  Hold that
reference across the instantiate and reject paths.  Drop the auth key
owning reference from revoke and destroy.

[jarkko: Replaced the first two paragraphs of text with an actual
 concurrency scenario.]

## References
- https://git.kernel.org/stable/c/35ab4db86774d82389e4b9559e26ab7f68d8e395
- https://git.kernel.org/stable/c/4982bfabce6b33b3c9eddb4fb900fe5568b7cf91
- https://git.kernel.org/stable/c/708709c65a1832a99b0eef8ae46e343ddaca3d06
- https://git.kernel.org/stable/c/7216ce8cb12fee44e309503955bb83806b106129
- https://git.kernel.org/stable/c/83c0a1cb296d955d5f4d1f0bd8a769ba8ed8c29f
- https://git.kernel.org/stable/c/d8274181b0f28d450b42489723a5ba81042158d7
- https://git.kernel.org/stable/c/f9b68632ac93cc742f2e411021c4dbfe452ea0c2
- https://git.kernel.org/stable/c/fd15b457a86939c38aa12116adabd8ff686c5e51
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63823.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63823
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
