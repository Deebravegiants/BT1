# [H] ksmbd: fix OOB write in QUERY_INFO for compound requests

## Summary
Severity: High
Advisory: CVE-2026-31432
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31432
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.143, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix OOB write in QUERY_INFO for compound requests

When a compound request such as READ + QUERY_INFO(Security) is received,
and the first command (READ) consumes most of the response buffer,
ksmbd could write beyond the allocated buffer while building a security
descriptor.

The root cause was that smb2_get_info_sec() checked buffer space using
ppntsd_size from xattr, while build_sec_desc() often synthesized a
significantly larger descriptor from POSIX ACLs.

This patch introduces smb_acl_sec_desc_scratch_len() to accurately
compute the final descriptor size beforehand, performs proper buffer
checking with smb2_calc_max_out_buf_len(), and uses exact-sized
allocation + iov pinning.

## References
- https://git.kernel.org/stable/c/075ea208c648cc2bcd616295b711d3637c61de45
- https://git.kernel.org/stable/c/515c2daab46021221bdf406bef19bc90a44ec617
- https://git.kernel.org/stable/c/850452af77f55d185f9445e1f7a1db53c5e4aad4
- https://git.kernel.org/stable/c/d48c64fb80ad78b3dd29fb7d79b6ec7bd72bfc09
- https://git.kernel.org/stable/c/fda9522ed6afaec45cabc198d8492270c394c7bc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31432.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31432
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
