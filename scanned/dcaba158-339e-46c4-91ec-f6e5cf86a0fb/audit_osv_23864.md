# [M] igmp: Fix data-races around sysctl_igmp_llm_reports.

## Summary
Severity: Medium
Advisory: CVE-2022-49590
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49590
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <4.9.325, >=4.10.0 <4.14.290, >=4.15.0 <4.19.254, >=4.20.0 <5.4.208, >=5.5.0 <5.10.134, >=5.11.0 <5.15.58, >=5.16.0 <5.18.15

## Details
In the Linux kernel, the following vulnerability has been resolved:

igmp: Fix data-races around sysctl_igmp_llm_reports.

While reading sysctl_igmp_llm_reports, it can be changed concurrently.
Thus, we need to add READ_ONCE() to its readers.

This test can be packed into a helper, so such changes will be in the
follow-up series after net is merged into net-next.

  if (ipv4_is_local_multicast(pmc->multiaddr) &&
      !READ_ONCE(net->ipv4.sysctl_igmp_llm_reports))

## References
- https://git.kernel.org/stable/c/1656ecaddf90e2a070ec2d2404cdae3edf80faca
- https://git.kernel.org/stable/c/260446eb8e5541402b271343a4516f2b33dec1e4
- https://git.kernel.org/stable/c/46307adceb67bdf2ec38408dd9cebc378a6b5c46
- https://git.kernel.org/stable/c/473aad9ad57ff760005377e6f45a2ad4210e08ce
- https://git.kernel.org/stable/c/a84b4afaca2573ed3aed1f8854aefe3ca5a82e72
- https://git.kernel.org/stable/c/d77969e7d4ccc26bf1f414a39ef35050a83ba6d5
- https://git.kernel.org/stable/c/ed876e99ccf417b8bd7fd8408ba5e8b008e46cc8
- https://git.kernel.org/stable/c/f6da2267e71106474fbc0943dc24928b9cb79119
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49590.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49590
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
