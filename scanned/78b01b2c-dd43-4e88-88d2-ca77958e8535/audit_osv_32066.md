# [H] media: venus: hfi_parser: add check to avoid out of bound access

## Summary
Severity: High
Advisory: CVE-2025-23157
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-23157
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: hfi_parser: add check to avoid out of bound access

There is a possibility that init_codecs is invoked multiple times during
manipulated payload from video firmware. In such case, if codecs_count
can get incremented to value more than MAX_CODEC_NUM, there can be OOB
access. Reset the count so that it always starts from beginning.

## References
- https://git.kernel.org/stable/c/172bf5a9ef70a399bb227809db78442dc01d9e48
- https://git.kernel.org/stable/c/1ad6aa1464b8a5ce5c194458315021e8d216108e
- https://git.kernel.org/stable/c/26bbedd06d85770581fda5d78e78539bb088fad1
- https://git.kernel.org/stable/c/2b8b9ea4e26a501eb220ea189e42b4527e65bdfa
- https://git.kernel.org/stable/c/53e376178ceacca3ef1795038b22fc9ef45ff1d3
- https://git.kernel.org/stable/c/b2541e29d82da8a0df728aadec3e0a8db55d517b
- https://git.kernel.org/stable/c/cb5be9039f91979f8a2fac29f529f746d7848f3e
- https://git.kernel.org/stable/c/d4d88ece4ba91df5b02f1d3f599650f9e9fc0f45
- https://git.kernel.org/stable/c/e5133a0b25463674903fdc0528e0a29b7267130e
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23157.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23157
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
