# [H] hsr: Prevent use after free in prp_create_tagged_frame()

## Summary
Severity: High
Advisory: CVE-2023-52846
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52846
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.201, >=5.11.0 <5.15.139, >=5.16.0 <6.1.63, >=6.2.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

hsr: Prevent use after free in prp_create_tagged_frame()

The prp_fill_rct() function can fail.  In that situation, it frees the
skb and returns NULL.  Meanwhile on the success path, it returns the
original skb.  So it's straight forward to fix bug by using the returned
value.

## References
- https://git.kernel.org/stable/c/1787b9f0729d318d67cf7c5a95f0c3dba9a7cc18
- https://git.kernel.org/stable/c/6086258bd5ea7b5c706ff62da42b8e271b2401db
- https://git.kernel.org/stable/c/876f8ab52363f649bcc74072157dfd7adfbabc0d
- https://git.kernel.org/stable/c/a1a485e45d24b1cd8fe834fd6f1b06e2903827da
- https://git.kernel.org/stable/c/d103fb6726904e353b4773188ee3d3acb4078363
- https://git.kernel.org/stable/c/ddf4e04e946aaa6c458b8b6829617cc44af2bffd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52846.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52846
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
