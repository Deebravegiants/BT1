# [H] media: venus: hfi: add a check to handle OOB in sfr region

## Summary
Severity: High
Advisory: CVE-2025-23159
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-23159
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.13.0 <5.4.293, >=5.5.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: hfi: add a check to handle OOB in sfr region

sfr->buf_size is in shared memory and can be modified by malicious user.
OOB write is possible when the size is made higher than actual sfr data
buffer. Cap the size to allocated size for such cases.

## References
- https://git.kernel.org/stable/c/1b8fb257234e7d2d4b3f48af07c5aa5e11c71634
- https://git.kernel.org/stable/c/4dd109038d513b92d4d33524ffc89ba32e02ba48
- https://git.kernel.org/stable/c/4e95233af57715d81830fe82b408c633edff59f4
- https://git.kernel.org/stable/c/530f623f56a6680792499a8404083e17f8ec51f4
- https://git.kernel.org/stable/c/5af611c70fb889d46d2f654b8996746e59556750
- https://git.kernel.org/stable/c/8879397c0da5e5ec1515262995e82cdfd61b282a
- https://git.kernel.org/stable/c/a062d8de0be5525ec8c52f070acf7607ec8cbfe4
- https://git.kernel.org/stable/c/d78a8388a27b265fcb2b8d064f088168ac9356b0
- https://git.kernel.org/stable/c/f4b211714bcc70effa60c34d9fa613d182e3ef1e
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/23xxx/CVE-2025-23159.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-23159
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
