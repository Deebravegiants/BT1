# [H] CVE-2020-15862

## Summary
Severity: High
Advisory: CVE-2020-15862
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-08-20
Source: https://osv.dev/vulnerability/CVE-2020-15862
Type: osv

## Details
Net-SNMP through 5.8 has Improper Privilege Management because SNMP WRITE access to the EXTEND MIB provides the ability to run arbitrary commands as root.

## References
- https://security-tracker.debian.org/tracker/CVE-2020-15862
- https://security.gentoo.org/glsa/202008-12
- https://security.netapp.com/advisory/ntap-20200904-0001/
- https://usn.ubuntu.com/4471-1/
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=965166
- https://github.com/net-snmp/net-snmp/commit/77f6c60f57dba0aaea5d8ef1dd94bcd0c8e6d205
- https://salsa.debian.org/debian/net-snmp/-/commit/fad8725402752746daf0a751dcff19eb6aeab52e
