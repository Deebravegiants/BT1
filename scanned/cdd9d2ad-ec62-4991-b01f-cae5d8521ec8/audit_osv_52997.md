# [M] CVE-2022-2503

## Summary
Severity: Medium
Advisory: CVE-2022-2503
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-12
Source: https://osv.dev/vulnerability/CVE-2022-2503
Type: osv

## Details
Dm-verity is used for extending root-of-trust to root filesystems. LoadPin builds on this property to restrict module/firmware loads to just the trusted root filesystem. Device-mapper table reloads currently allow users with root privileges to switch out the target with an equivalent dm-linear target and bypass verification till reboot. This allows root to bypass LoadPin and can be used to load untrusted and unverified kernel modules and firmware, which implies arbitrary kernel execution and persistence for peripherals that do not verify firmware updates. We recommend upgrading past commit 4caae58406f8ceb741603eee460d79bacca9b1b5

## References
- https://security.netapp.com/advisory/ntap-20230214-0005/
- https://github.com/google/security-research/security/advisories/GHSA-6vq3-w69p-w63m
