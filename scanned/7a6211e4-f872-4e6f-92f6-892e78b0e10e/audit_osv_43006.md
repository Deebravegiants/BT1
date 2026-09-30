# [H] octeontx2-af: fix VF bringup affecting PF promiscuous state

## Summary
Severity: High
Advisory: CVE-2026-72312
Ecosystem: Linux
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72312
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

octeontx2-af: fix VF bringup affecting PF promiscuous state

Mbox handling of nix_set_rx_mode for a VF with promiscuous and
all_multi flags set to false causes deletion of the PF's promiscuous
and allmulti MCAM rules. This occurs because the APIs that
enable/disable these rules operate only on the PF, even when the
mbox request is made via a VF interface.

Guard both rvu_npc_enable_allmulti_entry() and
rvu_npc_enable_promisc_entry() disable paths with an is_vf() check so
that a VF bringing up or tearing down its interface cannot inadvertently
clear the PF's MCAM rules.

## References
- https://git.kernel.org/stable/c/212c59e5e416859579272288fd325148fc316109
- https://git.kernel.org/stable/c/3cf83432e0561aef6d7ec2664909d12d0ff0ffc1
- https://git.kernel.org/stable/c/3de77d2f34c2bc2acaedabc2c5e0a561b85c283a
- https://git.kernel.org/stable/c/53e17d9ed779ad25870abb9c31bc294c71a2278c
- https://git.kernel.org/stable/c/daa2451640a3e0727fd598f5c2ccb8bb4d5a8b9c
- https://git.kernel.org/stable/c/fabb881df322da25442f98d23f5fa371e3c78ec4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72312.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72312
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
