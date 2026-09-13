# [C] CVE-2023-28879

## Summary
Severity: Critical
Advisory: CVE-2023-28879
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-31
Source: https://osv.dev/vulnerability/CVE-2023-28879
Type: osv

## Details
In Artifex Ghostscript through 10.01.0, there is a buffer overflow leading to potential corruption of data internal to the PostScript interpreter, in base/sbcp.c. This affects BCPEncode, BCPDecode, TBCPEncode, and TBCPDecode. If the write buffer is filled to one byte less than full, and one then tries to write an escaped character, two bytes are written.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DHJX62KSRIOBZA6FKONMJP7MEFY7LTH2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MADLP3GWJFLLFVNZGEDNPMDQR6CCXAHN/
- http://www.openwall.com/lists/oss-security/2023/04/12/4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CI6UCKM3XMK7PYNIRGAVDJ5VKN6XYZOE/
- https://git.ghostscript.com/?p=ghostpdl.git%3Ba=commit%3Bh=37ed5022cecd584de868933b5b60da2e995b3179
- https://lists.debian.org/debian-lts-announce/2023/04/msg00003.html
- https://security.gentoo.org/glsa/202309-03
- https://www.debian.org/security/2023/dsa-5383
- https://ghostscript.readthedocs.io/en/latest/News.html
- https://bugs.ghostscript.com/show_bug.cgi?id=706494
