# [H] firmware_loader: Block path traversal

## Summary
Severity: High
Advisory: CVE-2024-47742
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-47742
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.54, >=6.7.0 <6.10.13, >=6.11.0 <6.11.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

firmware_loader: Block path traversal

Most firmware names are hardcoded strings, or are constructed from fairly
constrained format strings where the dynamic parts are just some hex
numbers or such.

However, there are a couple codepaths in the kernel where firmware file
names contain string components that are passed through from a device or
semi-privileged userspace; the ones I could find (not counting interfaces
that require root privileges) are:

 - lpfc_sli4_request_firmware_update() seems to construct the firmware
   filename from "ModelName", a string that was previously parsed out of
   some descriptor ("Vital Product Data") in lpfc_fill_vpd()
 - nfp_net_fw_find() seems to construct a firmware filename from a model
   name coming from nfp_hwinfo_lookup(pf->hwinfo, "nffw.partno"), which I
   think parses some descriptor that was read from the device.
   (But this case likely isn't exploitable because the format string looks
   like "netronome/nic_%s", and there shouldn't be any *folders* starting
   with "netronome/nic_". The previous case was different because there,
   the "%s" is *at the start* of the format string.)
 - module_flash_fw_schedule() is reachable from the
   ETHTOOL_MSG_MODULE_FW_FLASH_ACT netlink command, which is marked as
   GENL_UNS_ADMIN_PERM (meaning CAP_NET_ADMIN inside a user namespace is
   enough to pass the privilege check), and takes a userspace-provided
   firmware name.
   (But I think to reach this case, you need to have CAP_NET_ADMIN over a
   network namespace that a special kind of ethernet device is mapped into,
   so I think this is not a viable attack path in practice.)

Fix it by rejecting any firmware names containing ".." path components.

For what it's worth, I went looking and haven't found any USB device
drivers that use the firmware loader dangerously.

## References
- https://git.kernel.org/stable/c/28f1cd94d3f1092728fb775a0fe26c5f1ac2ebeb
- https://git.kernel.org/stable/c/3d2411f4edcb649eaf232160db459bb4770b5251
- https://git.kernel.org/stable/c/6c4e13fdfcab34811c3143a0a03c05fec4e870ec
- https://git.kernel.org/stable/c/7420c1bf7fc784e587b87329cc6dfa3dca537aa4
- https://git.kernel.org/stable/c/9b1ca33ebd05b3acef5b976c04e5e791af93ce1b
- https://git.kernel.org/stable/c/a77fc4acfd49fc6076e565445b2bc5fdc3244da4
- https://git.kernel.org/stable/c/c30558e6c5c9ad6c86459d9acce1520ceeab9ea6
- https://git.kernel.org/stable/c/d1768e5535d3ded59f888637016e6f821f4e069f
- https://git.kernel.org/stable/c/f0e5311aa8022107d63c54e2f03684ec097d1394
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47742.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47742
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
