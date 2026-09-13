# [M] ALPINE-CVE-2020-25637

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-25637
Ecosystem: Alpine:v3.12
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-25637
Type: osv

## Affected
- Alpine:v3.12: `libvirt` — affected >=0 <6.6.0-r3

## Details
A double free memory issue was found to occur in the libvirt API, in versions before 6.8.0, responsible for requesting information about network interfaces of a running QEMU domain. This flaw affects the polkit access control driver. Specifically, clients connecting to the read-write socket with limited ACL permissions could use this flaw to crash the libvirt daemon, resulting in a denial of service, or potentially escalate their privileges on the system. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-25637
