# [M] CVE-2017-12843

## Summary
Severity: Medium
Advisory: CVE-2017-12843
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-08-22
Source: https://osv.dev/vulnerability/CVE-2017-12843
Type: osv

## Details
Cyrus IMAP before 3.0.3 allows remote authenticated users to write to arbitrary files via a crafted (1) SYNCAPPLY, (2) SYNCGET or (3) SYNCRESTORE command.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6M32R5QPCCNT57BVH3NPV5WVJFSTDP7Q/
- https://github.com/cyrusimap/cyrus-imapd/commit/53c4137bd924b954432c6c59da7572c4c5ffa901
- https://github.com/cyrusimap/cyrus-imapd/commit/5edadcfb83bf27107578830801817f9e6d0ad941
- https://www.cyrusimap.org/imap/download/release-notes/3.0/x/3.0.3.html
