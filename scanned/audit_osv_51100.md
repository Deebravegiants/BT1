# [M] CVE-2021-20292

## Summary
Severity: Medium
Advisory: CVE-2021-20292
Aliases: A-189986136, PUB-A-189986136
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-28
Source: https://osv.dev/vulnerability/CVE-2021-20292
Type: osv

## Details
There is a flaw reported in the Linux kernel in versions before 5.9 in drivers/gpu/drm/nouveau/nouveau_sgdma.c in nouveau_sgdma_create_ttm in Nouveau DRM subsystem. The issue results from the lack of validating the existence of an object prior to performing operations on the object. An attacker with a local account with a root privilege, can leverage this vulnerability to escalate privileges and execute code in the context of the kernel.

## References
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1939686
