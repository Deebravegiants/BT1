# [H] CVE-2022-0998

## Summary
Severity: High
Advisory: CVE-2022-0998
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-30
Source: https://osv.dev/vulnerability/CVE-2022-0998
Type: osv

## Details
An integer overflow flaw was found in the Linux kernel’s virtio device driver code in the way a user triggers the vhost_vdpa_config_validate function. This flaw allows a local user to crash or potentially escalate their privileges on the system.

## References
- https://lore.kernel.org/netdev/20220123001216.2460383-13-sashal%40kernel.org/
- https://security.netapp.com/advisory/ntap-20220513-0003/
- http://www.openwall.com/lists/oss-security/2022/04/02/1
