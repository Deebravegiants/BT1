# [M] CVE-2021-4147

## Summary
Severity: Medium
Advisory: CVE-2021-4147
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-03-25
Source: https://osv.dev/vulnerability/CVE-2021-4147
Type: osv

## Details
A flaw was found in the libvirt libxl driver. A malicious guest could continuously reboot itself and cause libvirtd on the host to deadlock or crash, resulting in a denial of service condition.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00000.html
- https://security.netapp.com/advisory/ntap-20220513-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=2034195
