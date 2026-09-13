# [H] usb: typec: fix potential out of bounds in ucsi_ccg_update_set_new_cam_cmd()

## Summary
Severity: High
Advisory: CVE-2024-50268
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50268
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.230, >=5.11.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: typec: fix potential out of bounds in ucsi_ccg_update_set_new_cam_cmd()

The "*cmd" variable can be controlled by the user via debugfs.  That means
"new_cam" can be as high as 255 while the size of the uc->updated[] array
is UCSI_MAX_ALTMODES (30).

The call tree is:
ucsi_cmd() // val comes from simple_attr_write_xsigned()
-> ucsi_send_command()
   -> ucsi_send_command_common()
      -> ucsi_run_command() // calls ucsi->ops->sync_control()
         -> ucsi_ccg_sync_control()

## References
- https://git.kernel.org/stable/c/3a2ba841659a0f15102585120dea75d8d5209616
- https://git.kernel.org/stable/c/604314ecd682913925980dc955caea2d036eab5f
- https://git.kernel.org/stable/c/69e19774f15e12dda6c6c58001d059e30895009b
- https://git.kernel.org/stable/c/7dd08a0b4193087976db6b3ee7807de7e8316f96
- https://git.kernel.org/stable/c/8f47984b35f3be0cfc652c2ca358d5768ea3456b
- https://git.kernel.org/stable/c/d76923164705821aa1b01b8d9d1741f20c654ab4
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50268.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50268
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
