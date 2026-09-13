# [H] CVE-2019-3890

## Summary
Severity: High
Advisory: CVE-2019-3890
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2019-08-01
Source: https://osv.dev/vulnerability/CVE-2019-3890
Type: osv

## Details
It was discovered evolution-ews before 3.31.3 does not check the validity of SSL certificates. An attacker could abuse this flaw to get confidential information by tricking the user into connecting to a fake server without the user noticing the difference.

## References
- https://access.redhat.com/errata/RHSA-2019:3699
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3890
- https://gitlab.gnome.org/GNOME/evolution-ews/issues/27
