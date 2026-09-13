# [M] CVE-2021-3559

## Summary
Severity: Medium
Advisory: CVE-2021-3559
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-24
Source: https://osv.dev/vulnerability/CVE-2021-3559
Type: osv

## Details
A flaw was found in libvirt in the virConnectListAllNodeDevices API in versions before 7.0.0. It only affects hosts with a PCI device and driver that supports mediated devices (e.g., GRID driver). This flaw could be used by an unprivileged client with a read-only connection to crash the libvirt daemon by executing the 'nodedev-list' virsh command. The highest threat from this vulnerability is to system availability.

## References
- https://security.netapp.com/advisory/ntap-20210706-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=1962306
