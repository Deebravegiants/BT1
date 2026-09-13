# [H] media: ttpci: fix two memleaks in budget_av_attach

## Summary
Severity: High
Advisory: CVE-2024-27073
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27073
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: ttpci: fix two memleaks in budget_av_attach

When saa7146_register_device and saa7146_vv_init fails, budget_av_attach
should free the resources it allocates, like the error-handling of
ttpci_budget_init does. Besides, there are two fixme comment refers to
such deallocations.

## References
- https://git.kernel.org/stable/c/1597cd1a88cfcdc4bf8b1b44cd458fed9a5a5d63
- https://git.kernel.org/stable/c/24e51d6eb578b82ff292927f14b9f5ec05a46beb
- https://git.kernel.org/stable/c/55ca0c7eae8499bb96f4e5d9b26af95e89c4e6a0
- https://git.kernel.org/stable/c/656b8cc123d7635dd399d9f02594f27aa797ac3c
- https://git.kernel.org/stable/c/7393c681f9aa05ffe2385e8716989565eed2fe06
- https://git.kernel.org/stable/c/910363473e4bf97da3c350e08d915546dd6cc30b
- https://git.kernel.org/stable/c/af37aed04997e644f7e1b52b696b62dcae3cc016
- https://git.kernel.org/stable/c/d0b07f712bf61e1a3cf23c87c663791c42e50837
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27073.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27073
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
