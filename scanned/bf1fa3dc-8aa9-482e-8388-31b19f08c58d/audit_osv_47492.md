# [H] CVE-2016-7032

## Summary
Severity: High
Advisory: CVE-2016-7032
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2016-7032
Type: osv

## Details
sudo_noexec.so in Sudo before 1.8.15 on Linux might allow local users to bypass intended noexec command restrictions via an application that calls the (1) system or (2) popen function.

## References
- https://usn.ubuntu.com/3968-3/
- https://www.sudo.ws/alerts/noexec_bypass.html
- http://rhn.redhat.com/errata/RHSA-2016-2872.html
- http://www.securityfocus.com/bid/95776
- https://bugzilla.redhat.com/show_bug.cgi?id=1372830
