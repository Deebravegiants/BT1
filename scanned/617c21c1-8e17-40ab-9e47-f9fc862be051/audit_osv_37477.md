# [H] openvswitch: validate MPLS set/set_masked payload length

## Summary
Severity: High
Advisory: CVE-2026-31679
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31679
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

openvswitch: validate MPLS set/set_masked payload length

validate_set() accepted OVS_KEY_ATTR_MPLS as variable-sized payload for
SET/SET_MASKED actions. In action handling, OVS expects fixed-size
MPLS key data (struct ovs_key_mpls).

Use the already normalized key_len (masked case included) and reject
non-matching MPLS action key sizes.

Reject invalid MPLS action payload lengths early.

## References
- https://git.kernel.org/stable/c/2ca33b88a79ca42f017ae0f7011280325655438e
- https://git.kernel.org/stable/c/4cae986225f8b8679ad86b924918e7d75a96aa61
- https://git.kernel.org/stable/c/546b68ac893595877ffbd7751e5c55fd1c43ede6
- https://git.kernel.org/stable/c/68f32ef0683c8d1c05cd2e4f16818fa63ff59c6f
- https://git.kernel.org/stable/c/8ed7b9930cbc3bc71f868fa79a68700ac88d586a
- https://git.kernel.org/stable/c/98de18d327ef8cbbb704980e359e4872d8c28997
- https://git.kernel.org/stable/c/bd50c7484c3bb34097571c1334174fb8b7408036
- https://git.kernel.org/stable/c/c1f97152df8dfb17e855ddf0fc409b7bd13e9700
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31679.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31679
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
