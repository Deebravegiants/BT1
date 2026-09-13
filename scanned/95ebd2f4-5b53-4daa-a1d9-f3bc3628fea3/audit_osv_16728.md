# [H] CVE-2019-9208

## Summary
Severity: High
Advisory: CVE-2019-9208
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-28
Source: https://osv.dev/vulnerability/CVE-2019-9208
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.12 and 2.6.0 to 2.6.6, the TCAP dissector could crash. This was addressed in epan/dissectors/asn1/tcap/tcap.cnf by avoiding NULL pointer dereferences.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00027.html
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=3d1b8004ed3a07422ca5d4e4ee8097150b934fd2
- https://usn.ubuntu.com/3986-1/
- https://www.oracle.com/security-alerts/cpujan2020.html
- http://www.securityfocus.com/bid/107203
- https://seclists.org/bugtraq/2019/Mar/35
- https://www.debian.org/security/2019/dsa-4416
- https://www.wireshark.org/security/wnpa-sec-2019-07.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=15464
