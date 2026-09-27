# [C] batman-adv: hold claim backbone gateways by reference

## Summary
Severity: Critical
Advisory: CVE-2026-31657
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31657
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.5.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: hold claim backbone gateways by reference

batadv_bla_add_claim() can replace claim->backbone_gw and drop the old
gateway's last reference while readers still follow the pointer.

The netlink claim dump path dereferences claim->backbone_gw->orig and
takes claim->backbone_gw->crc_lock without pinning the underlying
backbone gateway. batadv_bla_check_claim() still has the same naked
pointer access pattern.

Reuse batadv_bla_claim_get_backbone_gw() in both readers so they operate
on a stable gateway reference until the read-side work is complete.
This keeps the dump and claim-check paths aligned with the lifetime
rules introduced for the other BLA claim readers.

## References
- https://git.kernel.org/stable/c/1f2dc36c297d27733f1b380ea644cf15a361bd7b
- https://git.kernel.org/stable/c/2f55b58b5a0bbed192d60c444a45a49cdf1b545f
- https://git.kernel.org/stable/c/4dee4c0688443aaf5bbec74aa203c851d1d53c35
- https://git.kernel.org/stable/c/5202f071b367ffbc8e279fc7a00db14f5e587f52
- https://git.kernel.org/stable/c/69d1ce9c72eca91203ffdb8d08bacd511100aec6
- https://git.kernel.org/stable/c/7962b522222628596ca9ecc8722efc95367aadbd
- https://git.kernel.org/stable/c/82d8701b2c930d0e96b0dbc9115a218d791cb0d2
- https://git.kernel.org/stable/c/f4858832ddef2f39f21e30b7226bbcd3c4b2bc96
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31657.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31657
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
