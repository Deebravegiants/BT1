# [H] Use-after-free in Linux kernel's netfilter: nf_tables component

## Summary
Severity: High
Advisory: CVE-2023-3610
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-21
Source: https://osv.dev/vulnerability/CVE-2023-3610
Type: osv

## Details
A use-after-free vulnerability in the Linux kernel's netfilter: nf_tables component can be exploited to achieve local privilege escalation.

Flaw in the error handling of bound chains causes a use-after-free in the abort path of NFT_MSG_NEWRULE. The vulnerability requires CAP_NET_ADMIN to be triggered.

We recommend upgrading past commit 4bedf9eee016286c835e3d8fa981ddece5338795.

## References
- https://git.kernel.org
- https://kernel.dance/4bedf9eee016286c835e3d8fa981ddece5338795
- https://lists.debian.org/debian-lts-announce/2023/08/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3610.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3610
- https://security.netapp.com/advisory/ntap-20230818-0005/
- https://www.debian.org/security/2023/dsa-5461
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit?id=4bedf9eee016286c835e3d8fa981ddece5338795
