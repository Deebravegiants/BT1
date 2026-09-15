# [M] drm/amd/display: Atom Integrated System Info v2_2 for DCN35

## Summary
Severity: Medium
Advisory: CVE-2024-36897
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36897
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.15.159, >=5.16.0 <6.1.91, >=6.2.0 <6.6.31, >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Atom Integrated System Info v2_2 for DCN35

New request from KMD/VBIOS in order to support new UMA carveout
model. This fixes a null dereference from accessing
Ctx->dc_bios->integrated_info while it was NULL.

DAL parses through the BIOS and extracts the necessary
integrated_info but was missing a case for the new BIOS
version 2.3.

## References
- https://git.kernel.org/stable/c/02f5300f6827206f6e48a77f51e6264993695e5c
- https://git.kernel.org/stable/c/3c7013a87124bab54216d9b99f77e8b6de6fbc1a
- https://git.kernel.org/stable/c/7e3030774431eb093165a31baff040d35446fb8b
- https://git.kernel.org/stable/c/9a35d205f466501dcfe5625ca313d944d0ac2d60
- https://git.kernel.org/stable/c/c2797ec16d9072327e7578d09ee05bcab52fffd0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36897.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36897
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
