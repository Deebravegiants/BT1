# [H] sctp: validate Adaptation Indication parameter length

## Summary
Severity: High
Advisory: CVE-2026-80717
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80717
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: validate Adaptation Indication parameter length

The Adaptation Layer Indication parameter contains a fixed 32-bit
Adaptation Code Point after its parameter header. However,
sctp_verify_param() accepts a header-only parameter because the generic
parameter walker only requires the header to be present.

sctp_process_param() then reads adaptation_ind beyond the declared
parameter. When the malformed parameter is last in an INIT, the read
starts at the receive skb tail, and the value is copied into the state
cookie returned in the INIT ACK. This may disclose four receive-buffer
tail bytes.

Require the declared parameter length to match the fixed structure size
and abort the association through the existing invalid parameter length
path otherwise.

## References
- https://git.kernel.org/stable/c/17b412468c7a44f66a385bda48cdc1e94e39bd6d
- https://git.kernel.org/stable/c/4c92c601c061e5602db2edeea54fef74aa304027
- https://git.kernel.org/stable/c/5fd7cfc708dfc988ae9920c21075e6121bc89926
- https://git.kernel.org/stable/c/74b21f52c5c5a71a05c0ff70e513f4f04ff28b17
- https://git.kernel.org/stable/c/7b7e4e3640d57bd8857f0052c8b0d8ed4e5e954a
- https://git.kernel.org/stable/c/93942b5772e0eee4147d4799cc1b936ae12fa615
- https://git.kernel.org/stable/c/bfa28cf99eb4d096c87da939f54233444d209ca5
- https://git.kernel.org/stable/c/fa7861ddbe3b525b5d541c15c3953d3569e6eb0e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80717.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80717
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
