# [C] nvmet-tcp: add bounds checks in nvmet_tcp_build_pdu_iovec

## Summary
Severity: Critical
Advisory: CVE-2026-23112
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-23112
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.253, >=5.11.0 <5.15.200, >=5.16.0 <6.1.163, >=6.2.0 <6.6.124, >=6.7.0 <6.12.70, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-tcp: add bounds checks in nvmet_tcp_build_pdu_iovec

nvmet_tcp_build_pdu_iovec() could walk past cmd->req.sg when a PDU
length or offset exceeds sg_cnt and then use bogus sg->length/offset
values, leading to _copy_to_iter() GPF/KASAN. Guard sg_idx, remaining
entries, and sg->length/offset before building the bvec.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-253495.html
- https://git.kernel.org/stable/c/0b9981751be14b59b4473383c731c833738aebdb
- https://git.kernel.org/stable/c/1385be357e8acd09b36e026567f3a9d5c61139de
- https://git.kernel.org/stable/c/19672ae68d52ff75347ebe2420dde1b07adca09f
- https://git.kernel.org/stable/c/42afe8ed8ad2de9c19457156244ef3e1eca94b5d
- https://git.kernel.org/stable/c/52a0a98549344ca20ad81a4176d68d28e3c05a5c
- https://git.kernel.org/stable/c/ab200d71553bdcf4de554a5985b05b2dd606bc57
- https://git.kernel.org/stable/c/dca1a6ba0da9f472ef040525fab10fd9956db59f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23112.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23112
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
