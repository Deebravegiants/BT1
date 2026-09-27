# [H] CVE-2016-7952

## Summary
Severity: High
Advisory: CVE-2016-7952
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-13
Source: https://osv.dev/vulnerability/CVE-2016-7952
Type: osv

## Details
X.org libXtst before 1.2.3 allows remote X servers to cause a denial of service (infinite loop) via a reply in the (1) XRecordStartOfData, (2) XRecordEndOfData, or (3) XRecordClientDied category without a client sequence and with attached data.

## References
- http://www.openwall.com/lists/oss-security/2016/10/04/2
- http://www.openwall.com/lists/oss-security/2016/10/04/4
- http://www.securityfocus.com/bid/93375
- http://www.securitytracker.com/id/1036945
- https://cgit.freedesktop.org/xorg/lib/libXtst/commit/?id=9556ad67af3129ec4a7a4f4b54a0d59701beeae3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AFLHX7WNEUXXDAGR324T35L5P6RRR7GE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RVEUZRHYY3AJEKMFQ4DS7DX3Y2AICFP7/
- https://lists.x.org/archives/xorg-announce/2016-October/002720.html
