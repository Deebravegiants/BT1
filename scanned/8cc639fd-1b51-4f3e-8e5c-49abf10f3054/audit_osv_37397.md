# [C] ksmbd: replace hardcoded hdr2_len with offsetof() in smb2_calc_max_out_buf_len()

## Summary
Severity: Critical
Advisory: CVE-2026-31478
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31478
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.6.0 <6.12.80, >=6.7.0 <6.18.21, >=6.13.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: replace hardcoded hdr2_len with offsetof() in smb2_calc_max_out_buf_len()

After this commit (e2b76ab8b5c9 "ksmbd: add support for read compound"),
response buffer management was changed to use dynamic iov array.
In the new design, smb2_calc_max_out_buf_len() expects the second
argument (hdr2_len) to be the offset of ->Buffer field in the
response structure, not a hardcoded magic number.
Fix the remaining call sites to use the correct offsetof() value.

## References
- https://git.kernel.org/stable/c/0e55f63dd08f09651d39e1b709a91705a8a0ddcb
- https://git.kernel.org/stable/c/4cb537ae4f37d7d0f617815ed4bed7173fb50861
- https://git.kernel.org/stable/c/6aef1765d6807e0f027cd87f6ac973eb0879a46d
- https://git.kernel.org/stable/c/70b4c414889492c522b6e4331562360f49be2361
- https://git.kernel.org/stable/c/80824c7e527b70cf9039534e60aff592e8f209d1
- https://git.kernel.org/stable/c/9a7166f0ef8cbb7bb48dd05e2471d995566003f5
- https://git.kernel.org/stable/c/c3a89e3ec1ccf64fa6a34e391e1581ebbcba8683
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31478.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31478
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
