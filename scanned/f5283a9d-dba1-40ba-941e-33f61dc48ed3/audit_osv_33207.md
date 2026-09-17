# [M] ASoC: soc-core: care NULL dirver name on snd_soc_lookup_component_nolocked()

## Summary
Severity: Medium
Advisory: CVE-2025-39892
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2025-39892
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: soc-core: care NULL dirver name on snd_soc_lookup_component_nolocked()

soc-generic-dmaengine-pcm.c uses same dev for both CPU and Platform.
In such case, CPU component driver might not have driver->name, then
snd_soc_lookup_component_nolocked() will be NULL pointer access error.
Care NULL driver name.

	Call trace:
	 strcmp from snd_soc_lookup_component_nolocked+0x64/0xa4
	 snd_soc_lookup_component_nolocked from snd_soc_unregister_component_by_driver+0x2c/0x44
	 snd_soc_unregister_component_by_driver from snd_dmaengine_pcm_unregister+0x28/0x64
	 snd_dmaengine_pcm_unregister from devres_release_all+0x98/0xfc
	 devres_release_all from device_unbind_cleanup+0xc/0x60
	 device_unbind_cleanup from really_probe+0x220/0x2c8
	 really_probe from __driver_probe_device+0x88/0x1a0
	 __driver_probe_device from driver_probe_device+0x30/0x110
	driver_probe_device from __driver_attach+0x90/0x178
	__driver_attach from bus_for_each_dev+0x7c/0xcc
	bus_for_each_dev from bus_add_driver+0xcc/0x1ec
	bus_add_driver from driver_register+0x80/0x11c
	driver_register from do_one_initcall+0x58/0x23c
	do_one_initcall from kernel_init_freeable+0x198/0x1f4
	kernel_init_freeable from kernel_init+0x1c/0x12c
	kernel_init from ret_from_fork+0x14/0x28

## References
- https://git.kernel.org/stable/c/168873ca1799d3f23442b9e79eae55f907b9b126
- https://git.kernel.org/stable/c/1d282dcd46d972be338085ae9e217462b366ce6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39892.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39892
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
