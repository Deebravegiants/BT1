# [M] CVE-2023-33203

## Summary
Severity: Medium
Advisory: CVE-2023-33203
CVSS: 6.4 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-18
Source: https://osv.dev/vulnerability/CVE-2023-33203
Type: osv

## Details
The Linux kernel before 6.2.9 has a race condition and resultant use-after-free in drivers/net/ethernet/qualcomm/emac/emac.c if a physically proximate attacker unplugs an emac based device.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.2.9
- https://bugzilla.redhat.com/show_bug.cgi?id=2192667
- https://bugzilla.suse.com/show_bug.cgi?id=1210685
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6b6bc5b8bd2d4ca9e1efa9ae0f98a0b0687ace75
