# [H] idpf: avoid vport access in idpf_get_link_ksettings

## Summary
Severity: High
Advisory: CVE-2024-50274
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50274
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

idpf: avoid vport access in idpf_get_link_ksettings

When the device control plane is removed or the platform
running device control plane is rebooted, a reset is detected
on the driver. On driver reset, it releases the resources and
waits for the reset to complete. If the reset fails, it takes
the error path and releases the vport lock. At this time if the
monitoring tools tries to access link settings, it call traces
for accessing released vport pointer.

To avoid it, move link_speed_mbps to netdev_priv structure
which removes the dependency on vport pointer and the vport lock
in idpf_get_link_ksettings. Also use netif_carrier_ok()
to check the link status and adjust the offsetof to use link_up
instead of link_speed_mbps.

## References
- https://git.kernel.org/stable/c/81d2fb4c7c18a3b36ba3e00b9d5b753107472d75
- https://git.kernel.org/stable/c/fa4d906ad0fb63a980a1d586a061c78ea1a345ba
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50274.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50274
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
