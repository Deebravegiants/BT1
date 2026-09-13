# [M] CVE-2013-7449

## Summary
Severity: Medium
Advisory: CVE-2013-7449
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2016-04-21
Source: https://osv.dev/vulnerability/CVE-2013-7449
Type: osv

## Details
The ssl_do_connect function in common/server.c in HexChat before 2.10.2, XChat, and XChat-GNOME does not verify that the server hostname matches a domain name in the X.509 certificate, which allows man-in-the-middle attackers to spoof SSL servers via an arbitrary valid certificate.

## References
- http://hexchat.readthedocs.org/en/latest/changelog.html
- http://www.ubuntu.com/usn/USN-2945-1
- https://github.com/hexchat/hexchat/commit/c9b63f7f9be01692b03fa15275135a4910a7e02d
- https://bugzilla.redhat.com/show_bug.cgi?id=1081839
- https://github.com/hexchat/hexchat/issues/524
