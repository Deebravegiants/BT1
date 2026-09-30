# [M] CVE-2019-19067

## Summary
Severity: Medium
Advisory: CVE-2019-19067
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19067
Type: osv

## Details
Four memory leaks in the acp_hw_init() function in drivers/gpu/drm/amd/amdgpu/amdgpu_acp.c in the Linux kernel before 5.3.8 allow attackers to cause a denial of service (memory consumption) by triggering mfd_add_hotplug_devices() or pm_genpd_add_device() failures, aka CID-57be09c6e874. NOTE: third parties dispute the relevance of this because the attacker must already have privileges for module loading

## References
- https://usn.ubuntu.com/4526-1/
- https://usn.ubuntu.com/4208-1/
- https://usn.ubuntu.com/4226-1/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.8
- https://bugzilla.suse.com/show_bug.cgi?id=1157180
- https://github.com/torvalds/linux/commit/57be09c6e8747bf48704136d9e3f92bfb93f5725
