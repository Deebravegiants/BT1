# [H] can: m_can: m_can_tx_handler(): fix use after free of skb

## Summary
Severity: High
Advisory: CVE-2022-49275
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49275
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.18.0 <4.9.324, >=4.10.0 <4.14.289, >=4.15.0 <4.19.253, >=4.20.0 <5.4.207, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: m_can: m_can_tx_handler(): fix use after free of skb

can_put_echo_skb() will clone skb then free the skb. Move the
can_put_echo_skb() for the m_can version 3.0.x directly before the
start of the xmit in hardware, similar to the 3.1.x branch.

## References
- https://git.kernel.org/stable/c/08d90846e438ac22dc56fc49ec0b0d195831c5ed
- https://git.kernel.org/stable/c/2e8e79c416aae1de224c0f1860f2e3350fa171f8
- https://git.kernel.org/stable/c/31417073493f302d26ab66b3abc098d43227b835
- https://git.kernel.org/stable/c/4db7d6f481990dd179a9ee7126dc7aa31ea4fff3
- https://git.kernel.org/stable/c/7728d937ec403a1ceff9483023252d2cb8777f81
- https://git.kernel.org/stable/c/869016a2938ac44f7b2fb7fc22c89edad99eb9b3
- https://git.kernel.org/stable/c/d3892a747ab16b1eb6593a19d29f62c3b3f020ac
- https://git.kernel.org/stable/c/d93ed9aff64968f4cdad690712eb4f48ae537bde
- https://git.kernel.org/stable/c/f43e64076ff1b1dcb893fb77ad1204105f710a29
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49275.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49275
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
