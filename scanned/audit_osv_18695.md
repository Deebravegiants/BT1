# [M] CVE-2020-35503

## Summary
Severity: Medium
Advisory: CVE-2020-35503
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2020-35503
Type: osv

## Details
A NULL pointer dereference flaw was found in the megasas-gen2 SCSI host bus adapter emulation of QEMU in versions before and including 6.0. This issue occurs in the megasas_command_cancelled() callback function while dropping a SCSI request. This flaw allows a privileged guest user to crash the QEMU process on the host, resulting in a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://security.netapp.com/advisory/ntap-20210720-0008/
- https://bugzilla.redhat.com/show_bug.cgi?id=1910346
