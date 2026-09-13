# [M] CVE-2016-0771

## Summary
Severity: Medium
Advisory: CVE-2016-0771
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2016-03-13
Source: https://osv.dev/vulnerability/CVE-2016-0771
Type: osv

## Details
The internal DNS server in Samba 4.x before 4.1.23, 4.2.x before 4.2.9, 4.3.x before 4.3.6, and 4.4.x before 4.4.0rc4, when an AD DC is configured, allows remote authenticated users to cause a denial of service (out-of-bounds read) or possibly obtain sensitive information from process memory by uploading a crafted DNS TXT record.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00063.html
- http://www.securityfocus.com/bid/84273
- http://www.securitytracker.com/id/1035219
- http://www.debian.org/security/2016/dsa-3514
- http://www.ubuntu.com/usn/USN-2922-1
- https://www.samba.org/samba/security/CVE-2016-0771.html
- https://bugzilla.samba.org/show_bug.cgi?id=11128
- https://bugzilla.samba.org/show_bug.cgi?id=11686
