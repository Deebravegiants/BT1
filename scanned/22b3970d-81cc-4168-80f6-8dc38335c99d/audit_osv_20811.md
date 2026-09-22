# [M] CVE-2021-3735

## Summary
Severity: Medium
Advisory: CVE-2021-3735
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-26
Source: https://osv.dev/vulnerability/CVE-2021-3735
Type: osv

## Details
A deadlock issue was found in the AHCI controller device of QEMU. It occurs on a software reset (ahci_reset_port) while handling a host-to-device Register FIS (Frame Information Structure) packet from the guest. A privileged user inside the guest could use this flaw to hang the QEMU process on the host, resulting in a denial of service condition. The highest threat from this vulnerability is to system availability.

## References
- https://access.redhat.com/security/cve/CVE-2021-3735
- https://security-tracker.debian.org/tracker/CVE-2021-3735
- https://security.netapp.com/advisory/ntap-20250228-0009/
- https://bugzilla.redhat.com/show_bug.cgi?id=1997184
