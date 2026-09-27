# [M] CVE-2020-14301

## Summary
Severity: Medium
Advisory: CVE-2020-14301
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-27
Source: https://osv.dev/vulnerability/CVE-2020-14301
Type: osv

## Details
An information disclosure vulnerability was found in libvirt in versions before 6.3.0. HTTP cookies used to access network-based disks were saved in the XML dump of the guest domain. This flaw allows an attacker to access potentially sensitive information in the domain configuration via the `dumpxml` command.

## References
- https://security.netapp.com/advisory/ntap-20210629-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=1848640
