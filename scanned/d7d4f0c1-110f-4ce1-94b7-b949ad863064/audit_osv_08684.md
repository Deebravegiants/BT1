# [H] CVE-2016-5301

## Summary
Severity: High
Advisory: CVE-2016-5301
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-30
Source: https://osv.dev/vulnerability/CVE-2016-5301
Type: osv

## Details
The parse_chunk_header function in libtorrent before 1.1.1 allows remote attackers to cause a denial of service (crash) via a crafted (1) HTTP response or possibly a (2) UPnP broadcast.

## References
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00079.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00103.html
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00043.html
- http://www.openwall.com/lists/oss-security/2016/06/04/9
- http://www.openwall.com/lists/oss-security/2016/06/05/1
- http://www.securityfocus.com/bid/91498
- https://github.com/arvidn/libtorrent/pull/782/files
- https://github.com/arvidn/libtorrent/issues/780
