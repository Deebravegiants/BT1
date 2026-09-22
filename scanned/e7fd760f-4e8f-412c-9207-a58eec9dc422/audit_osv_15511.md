# [M] CVE-2019-16935

## Summary
Severity: Medium
Advisory: CVE-2019-16935
Aliases: PSF-2019-6
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2019-09-28
Source: https://osv.dev/vulnerability/CVE-2019-16935
Type: osv

## Details
The documentation XML-RPC server in Python through 2.7.16, 3.x through 3.6.9, and 3.7.x through 3.7.4 has XSS via the server_title field. This occurs in Lib/DocXMLRPCServer.py in Python 2.x, and in Lib/xmlrpc/server.py in Python 3.x. If set_server_title is called with untrusted input, arbitrary JavaScript can be delivered to clients that visit the http URL for this server.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4X3HW5JRZ7GCPSR7UHJOLD7AWLTQCDVR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BEARDOTXCYPYELKBD2KWZ27GSPXDI3GQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/COATURTCY7G67AYI6UDV5B2JZTBCKIDX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JCPGLTTOBB3QEARDX4JOYURP6ELNNA2V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K7HNVIFMETMFWWWUNTB72KYJYXCZOS5V/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/M34WOYCDKTDE5KLUACE2YIEH7D37KHRX/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OYGESQSGIHDCIGOBVF7VXCMIE6YDWRYB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZBTGPBUABGXZ7WH7677OEM3NSP6ZEA76/
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00062.html
- http://lists.opensuse.org/opensuse-security-announce/2019-10/msg00063.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00040.html
- https://github.com/python/cpython/blob/35c0809158be7feae4c4f877a08b93baea2d8291/Lib/xmlrpc/server.py#L897
- https://github.com/python/cpython/blob/e007860b8b3609ce0bc62b1780efaa06241520bd/Lib/DocXMLRPCServer.py#L213
- https://lists.debian.org/debian-lts-announce/2020/07/msg00011.html
- https://lists.debian.org/debian-lts-announce/2021/04/msg00015.html
- https://security.netapp.com/advisory/ntap-20191017-0004/
- https://usn.ubuntu.com/4151-1/
- https://usn.ubuntu.com/4151-2/
